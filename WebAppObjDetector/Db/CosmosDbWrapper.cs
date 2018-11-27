using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Azure.Documents;
using Microsoft.Azure.Documents.Client;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using WebAppObjectDetector.Models;

// https://dzone.com/articles/a-few-great-ways-to-consume-restful-apis-in-c
// https://code-maze.com/different-ways-consume-restful-api-csharp/#HttpWebRequest 

namespace WebAppObjectDetector.Db
{
    public static class CosmosDbWrapper
    {

        // for us the collection settings keeps on changing. 
        //private static readonly string CollectionId = ConfigurationManager.AppSettings["collection"];
        
        private static HttpClient _httpClient;
        private static string _commonURL; 

        public static void Initialize()
        {
            _httpClient = new HttpClient();
            _httpClient.DefaultRequestHeaders.Add("User-Agent", "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36");
            _commonURL = "http://localhost:5001/comsosDB/v1.0/"; 
        }



        public static List<GenericItems> GetCollection()
        {
            List<GenericItems> rv = new List<GenericItems>();
 
            var url = _commonURL+ "collections"; 
            var response = _httpClient.GetStringAsync(new Uri(url)).Result;
            JObject o = JObject.Parse(response);
            // the result is returned in the Json format. but the first item is result. 
            JToken t = o.GetValue("result");
            if (t != null)
            {
                foreach (var item in t)
                {
                    {
                        GenericItems gitem = JsonConvert.DeserializeObject<GenericItems>(item.ToString());
                        Debug.Assert(gitem != null);
                        rv.Add(gitem);
                        Debug.WriteLine(gitem.Id);
                        Debug.WriteLine(gitem.SelfLink);
                    }
                }
            }
            return rv;
        }

        public static List<OpenCVDetectedItems> GetOpenCVDetectedItemsDocument(string docId)
        {
            List<OpenCVDetectedItems> rv = new List<OpenCVDetectedItems>();
            string strUrlEncoded = Uri.EscapeDataString(docId);

            // [ay attention, the url does not have ending /
            var url = _commonURL + "document?docId=" +strUrlEncoded;
            var response = _httpClient.GetStringAsync(new Uri(url)).Result;
            JObject o = JObject.Parse(response);

            OpenCVResult rvObj = JsonConvert.DeserializeObject<OpenCVResult>(o.ToString());
            if (rvObj != null)
            {
                if (rvObj.detectedItems != null)
                {
                    rv = rvObj.detectedItems.ToList();
                }

            }
            return rv;
        }


        //public static List<Document> GetDocuments(string CollectionId)
        //{
        //    List<Document> docColl = client.CreateDocumentQuery(CollectionId).ToList();
        //    return docColl;
        //}
        /// <summary>
        /// Returns the Json implementation of the documents found in an collection. 
        /// TODO:: HORRIBLY, need to convert Json to string and then to Json again. WHY oh WHY!!!
        /// </summary>
        /// <param name="CollectionId"></param>
        /// <returns></returns>
        //public static async Task<string> GetDocumentsDynamic(string CollectionId)
        //{

        //    ////List<GenericItems> rv = new List<GenericItems>();

        //    ////var url = "http://localhost:5000/comsosDB/v1.0/documents";

        //    ////string jSonBody = "{\"collectionLink\":" + "\"" + CollectionId + "\"" + "}";
        //    ////_httpClient.
        //    ////var response = _httpClient.GetStringAsync(new Uri(url)).Result;
        //    ////JObject o = JObject.Parse(response);
        //    ////// the result is returned in the Json format. but the first item is result. 
        //    ////JToken t = o.GetValue("result");
        //    ////if (t != null)
        //    ////{
        //    ////    foreach (var item in t)
        //    ////    {
        //    ////        {
        //    ////            GenericItems gitem = JsonConvert.DeserializeObject<GenericItems>(item.ToString());
        //    ////            Debug.Assert(gitem != null);
        //    ////            rv.Add(gitem);
        //    ////            Debug.WriteLine(gitem.Id);
        //    ////            Debug.WriteLine(gitem.SelfLink);
        //    ////        }
        //    ////    }
        //    ////}
        //    ////return rv;



        //    //StringBuilder sb = new StringBuilder();
        //    //sb.Append("[");
        //    //bool bFirstTime = true; 
            
        //    //foreach (Document document in await client.ReadDocumentFeedAsync(CollectionId, new FeedOptions { MaxItemCount = 6 }))
        //    //{
        //    //    if (bFirstTime)
        //    //    {
        //    //        bFirstTime = false; 
        //    //    }
        //    //    else
        //    //    {
        //    //        sb.Append(",");
        //    //    }

                
        //    //    string Provider = document.GetPropertyValue<String>("id");
        //    //    switch (Provider)
        //    //    {
        //    //        case "openCVPhotoExtractor":
        //    //            {
        //    //                OpenCVResult result = JsonConvert.DeserializeObject<OpenCVResult>(document.ToString());
        //    //                Console.WriteLine("openCVPhotoExtractor");
        //    //                sb.Append(JsonConvert.SerializeObject(result));
        //    //                break;
        //    //            }
        //    //        case "yoloBirdImageDetector":
        //    //            {
        //    //                YoloDetector result = JsonConvert.DeserializeObject<YoloDetector>(document.ToString());
        //    //                Console.WriteLine("yoloBirdImageDetector");
        //    //                sb.Append(JsonConvert.SerializeObject(result));
        //    //                break;
        //    //            }
        //    //        case "mobileNetImageDetector":
        //    //            {
        //    //                mobileDetector result = JsonConvert.DeserializeObject<mobileDetector>(document.ToString());
        //    //                Console.WriteLine("mobileNetImageDetector");
        //    //                sb.Append(JsonConvert.SerializeObject(result));
        //    //                break;
        //    //            }
        //    //        case "azureImageDetector":
        //    //            {
        //    //                azureDetector result = JsonConvert.DeserializeObject<azureDetector>(document.ToString());
        //    //                Console.WriteLine("azureImageDetector");
        //    //                sb.Append(JsonConvert.SerializeObject(result));
        //    //                break;
        //    //            }
        //    //        case "googleImageDetector":
        //    //            {
        //    //                googleDetector result = JsonConvert.DeserializeObject<googleDetector>(document.ToString());
        //    //                Console.WriteLine("googleImageDetector");
        //    //                sb.Append(JsonConvert.SerializeObject(result));
        //    //                break;
        //    //            }

        //    //        case "ListContainingSomewhatTrueImages":
        //    //            {
        //    //                ListOfLabelledImages result = JsonConvert.DeserializeObject<ListOfLabelledImages>(document.ToString());
        //    //                Console.WriteLine("ListOfLabelledImages");
        //    //                sb.Append(JsonConvert.SerializeObject(result));
        //    //                break;
        //    //            }

        //    //        default:
        //    //            {
        //    //                Object result = JsonConvert.DeserializeObject<Object>(document.ToString());
        //    //                Console.WriteLine("Default");
        //    //                sb.Append(JsonConvert.SerializeObject(result));
        //    //                Console.WriteLine("unknown provider");
        //    //                break;
        //    //            }
        //    //    }

        //    }

            //sb.Append("]");

            //return sb.ToString();
        
    }
}
