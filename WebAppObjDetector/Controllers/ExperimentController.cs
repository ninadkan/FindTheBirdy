using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;
using Microsoft.Azure.Documents;
using WebAppObjectDetector.Db;
using WebAppObjectDetector.Models;

namespace WebAppObjectDetector.Controllers
{
    public class ExperimentController : Controller
    {

        public ActionResult Index()
        {
            var items = CosmosDbWrapper.GetCollection();
        

            if (items != null && items.Count > 0)
            {
                List<SelectListItem> expColl = items.Select(x => new SelectListItem() { Text = x.Id, Value = x.SelfLink }).ToList();
                SelectList selList = new SelectList(expColl, "Value", "Text");
                ViewBag.ExperimentCollectionVB = selList;
                return View("SinglePageView");
            }
            return View();
        }

        public IActionResult CopyFilesAndCreateExperiment()
        {
            return View(); 
        }


        public IActionResult ImageMaskTag()
        {
            return View();
        }


        #region AJAX calls

        //[HttpPost]
        //public async Task<string> GetDocumentRecords(int Id, [FromBody] CollectionIdWrapper CollectionId)
        //{
        //    string strRV = string.Empty;

        //    //string CollectionId = "/" + dbs + "/" + dbCollId + "/" + colls + "/" + collId+ "/"; 
        //    //if (CollectionId != null && !string.IsNullOrEmpty(CollectionId.CollectionId))
        //    //{
        //    //    List<Document> docColl = CosmosDbWrapper.GetDocuments(CollectionId.CollectionId);
        //    //    if (docColl != null && docColl.Count > 0)
        //    //    {
        //    //        foreach (Document d in docColl)
        //    //        {
        //    //            string Provider = d.GetPropertyValue<String>("provider");
        //    //            Console.WriteLine(Provider);
        //    //        }
        //    //    }
        //    //}

        //    strRV = await CosmosDbWrapper.GetDocumentsDynamic(CollectionId.CollectionId);
        //    // its got \r\n in the strRV. That needs to be replaced
        //    strRV = strRV.Replace("\r\n ", "");

        //    for (int i = 0; i < 10; i++)
        //    {
        //        Debug.WriteLine("i = " + i.ToString() + "Value = " + strRV[i]);
        //    }


        //    strRV = strRV.Replace("\\\"", "\"");

        //    for (int i = 0; i < 10; i++)
        //    {
        //        Debug.WriteLine("i = " + i.ToString() + "Value = " + strRV[i]);
        //    }

        //    return strRV;
        //}




        public ActionResult GetDetails(string provider, string docId, string collectionId)
        {
            string strRV = string.Empty;
            switch (provider)
            {
                case "openCVPhotoExtractor":
                    {
                        var docs = CosmosDbWrapper.GetOpenCVDetectedItemsDocument(docId);

                        List<SelectListItem> expColl = docs.Select(x => new SelectListItem() { Text = x.openCVDetectedImageName, Value = x.openCVDetectedImageName }).ToList();
                        SelectList selList = new SelectList(expColl, "Value", "Text");
                        ViewBag.ExperimentCollectionVB = selList;
                        ViewBag.CollectionId = collectionId; 

                        return View("DisplayAndLabelSelectedImages", docs);
                    }
                //case "yoloBirdImageDetector":
                //    {
                //        YoloDetector result = JsonConvert.DeserializeObject<YoloDetector>(document.ToString());
                //        Console.WriteLine("yoloBirdImageDetector");
                //        sb.Append(JsonConvert.SerializeObject(result));
                //        break;
                //    }
                //case "mobileNetImageDetector":
                //    {
                //        mobileDetector result = JsonConvert.DeserializeObject<mobileDetector>(document.ToString());
                //        Console.WriteLine("mobileNetImageDetector");
                //        sb.Append(JsonConvert.SerializeObject(result));
                //        break;
                //    }
                //case "azureImageDetector":
                //    {
                //        azureDetector result = JsonConvert.DeserializeObject<azureDetector>(document.ToString());
                //        Console.WriteLine("azureImageDetector");
                //        sb.Append(JsonConvert.SerializeObject(result));
                //        break;
                //    }
                //case "googleImageDetector":
                //    {
                //        googleDetector result = JsonConvert.DeserializeObject<googleDetector>(document.ToString());
                //        Console.WriteLine("googleImageDetector");
                //        sb.Append(JsonConvert.SerializeObject(result));
                //        break;
                //    }

                //case "ListContainingSomewhatTrueImages":
                //    {
                //        ListOfLabelledImages result = JsonConvert.DeserializeObject<ListOfLabelledImages>(document.ToString());
                //        Console.WriteLine("ListOfLabelledImages");
                //        sb.Append(JsonConvert.SerializeObject(result));
                //        break;
                //    }

                //default:
                //    {
                //        Object result = JsonConvert.DeserializeObject<Object>(document.ToString());
                //        Console.WriteLine("Default");
                //        sb.Append(JsonConvert.SerializeObject(result));
                //        Console.WriteLine("unknown provider");
                //        break;
                //    }
            }
            return View();
        }

        #endregion
    }


}
