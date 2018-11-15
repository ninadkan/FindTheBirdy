using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Newtonsoft.Json; 

namespace WebApplication1.Models
{

    public class GenericItems
    {
        [JsonProperty(PropertyName = "id")]
        public string Id;
        [JsonProperty(PropertyName = "_self")]
        public string SelfLink;
    }
 
    public class CollectionIdWrapper
    {
        public string CollectionId { get; set; }
    }
 
    public class DetectedItems
    {
        [JsonProperty(PropertyName = "ImageName")] 
        public string ImageName {get; set;}
        [JsonProperty(PropertyName = "ConfidenceSore")] 
        public string ConfidenceSore {get; set;}
        [JsonProperty(PropertyName = "Hint")] 
        public string Hint {get; set;}
    }

    public class YoloDetector
    {
        [JsonProperty(PropertyName = "id")] 
         public string id {get; set;}
        [JsonProperty(PropertyName = "DateTime")] 
         public string DateTime {get; set;}
        [JsonProperty(PropertyName = "elapsedTime")] 
         public string elapsedTime {get; set;}
        [JsonProperty(PropertyName = "result - totalNumberOfRecords")] 
         public string resulttotalNumberOfRecords {get; set;}
        [JsonProperty(PropertyName = "result - birdFound")] 
         public string resultbirdFound {get; set;}
        [JsonProperty(PropertyName = "param - confThreshold")] 
         public string paramconfThreshold {get; set;}
        [JsonProperty(PropertyName = "param - shapeWeight")] 
         public string paramshapeWeight {get; set;}
        [JsonProperty(PropertyName = "param - scaleFactor")] 
         public string paramscaleFactor {get; set;}
        [JsonProperty(PropertyName = "param - numberOfIterations")] 
         public string paramnumberOfIterations {get; set;}
        [JsonProperty(PropertyName = "param - imageTag")] 
         public string paramimageTag {get; set;}
        [JsonProperty(PropertyName = "param - nmsThreshold")] 
         public string paramnmsThreshold {get; set;}
        [JsonProperty(PropertyName = "detectedItems")]
        public DetectedItems[] detectedItems { get; set; }
        [JsonProperty(PropertyName = "_self")]
        public string SelfLink { get; set; }
    }


    public class googleDetector
    {
        [JsonProperty(PropertyName = "id")] 
        public string id {get; set;}
        [JsonProperty(PropertyName = "DateTime")] 
        public string DateTime {get; set;}
        [JsonProperty(PropertyName = "elapsedTime")] 
        public string elapsedTime {get; set;}
        [JsonProperty(PropertyName = "result - totalNumberOfRecords")] 
        public string resulttotalNumberOfRecords {get; set;}
        [JsonProperty(PropertyName = "result - birdFound")] 
        public string resultbirdFound {get; set;}
        [JsonProperty(PropertyName = "param - confThreshold")] 
        public string paramconfThreshold {get; set;}
        [JsonProperty(PropertyName = "param - numberOfIterations")] 
        public string paramnumberOfIterations {get; set;}
        [JsonProperty(PropertyName = "param - imageTag")] 
        public string paramimageTag {get; set;}
        [JsonProperty(PropertyName = "detectedItems")]
        public DetectedItems[] detectedItems { get; set; }
        [JsonProperty(PropertyName = "_self")]
        public string SelfLink { get; set; }
    }

    public class azureDetector
    {
        [JsonProperty(PropertyName = "id")] 
         public string id {get; set;}
        [JsonProperty(PropertyName = "DateTime")] 
         public string DateTime {get; set;}
        [JsonProperty(PropertyName = "elapsedTime")] 
         public string elapsedTime {get; set;}
        [JsonProperty(PropertyName = "result - totalNumberOfRecords")] 
         public string resulttotalNumberOfRecords {get; set;}
        [JsonProperty(PropertyName = "result - birdFound")] 
         public string resultbirdFound {get; set;}
        [JsonProperty(PropertyName = "result - Hint bird Found")] 
         public string resultHintbirdFound {get; set;}
        [JsonProperty(PropertyName = "param - confThreshold")] 
         public string paramconfThreshold {get; set;}
        [JsonProperty(PropertyName = "param - numberOfIterations")] 
         public string paramnumberOfIterations {get; set;}
        [JsonProperty(PropertyName = "param - imageTag")] 
         public string paramimageTag {get; set;}
        [JsonProperty(PropertyName = "detectedItems")] 
         public DetectedItems[] detectedItems {get; set;}
        [JsonProperty(PropertyName = "_self")]
        public string SelfLink { get; set; }
    }

    public class mobileDetector
    {
        [JsonProperty(PropertyName = "id")] 
         public string id {get; set;}
         [JsonProperty(PropertyName = "DateTime")] 
         public string DateTime {get; set;}
         [JsonProperty(PropertyName = "elapsedTime")] 
         public string elapsedTime {get; set;}
         [JsonProperty(PropertyName = "result - totalNumberOfRecords")] 
         public string resulttotalNumberOfRecords {get; set;}
         [JsonProperty(PropertyName = "result - birdFound")] 
         public string resultbirdFound {get; set;}
         [JsonProperty(PropertyName = "param - confThreshold")] 
         public string paramconfThreshold {get; set;}
         [JsonProperty(PropertyName = "param - shapeWeight")] 
         public string paramshapeWeight {get; set;}
         [JsonProperty(PropertyName = "param - scaleFactor")] 
         public string paramscaleFactor {get; set;}
         [JsonProperty(PropertyName = "param - numberOfIterations")] 
         public string paramnumberOfIterations {get; set;}
         [JsonProperty(PropertyName = "param - imageTag")] 
         public string paramimageTag {get; set;}
         [JsonProperty(PropertyName = "detectedItems")]
         public DetectedItems[] detectedItems { get; set; }
        [JsonProperty(PropertyName = "_self")]
        public string SelfLink { get; set; }
    }

    public class OpenCVResult
    {
        [JsonProperty(PropertyName = "id")] 
        public string id {get; set;}
        [JsonProperty(PropertyName = "DateTime")] 
        public string DateTime {get; set;}
        [JsonProperty(PropertyName = "result-totalNumberOfRecords")] 
        public string resulttotalNumberOfRecords {get; set;}
        [JsonProperty(PropertyName = "TotalNumberOfImagesDetected")] 
        public string TotalNumberOfImagesDetected {get; set;}
        [JsonProperty(PropertyName = "param-historyImage")] 
        public string paramhistoryImage {get; set;}
        [JsonProperty(PropertyName = "param-varThreshold")] 
        public string paramvarThreshold {get; set;}
        [JsonProperty(PropertyName = "param-numberOfIterations")] 
        public string paramnumberOfIterations {get; set;}
        [JsonProperty(PropertyName = "param-boundingRectAreaThreshold")] 
        public string paramboundingRectAreaThreshold {get; set;}
        [JsonProperty(PropertyName = "param-contourCountThreshold")] 
        public string paramcontourCountThreshold {get; set;}
        [JsonProperty(PropertyName = "param-maskDiffThreshold")] 
        public string parammaskDiffThreshold {get; set;}
        [JsonProperty(PropertyName = "param-partOfFileName")] 
        public string parampartOfFileName {get; set;}
        [JsonProperty(PropertyName = "detectedItems")] 
        public OpenCVDetectedItems[] detectedItems {get; set;}
        [JsonProperty(PropertyName = "_self")]
        public string SelfLink { get; set; }
    }


    public class OpenCVDetectedItems
    {
        [JsonProperty(PropertyName = "openCVDetectedImageName")] 
         public string openCVDetectedImageName {get; set;}
        [JsonProperty(PropertyName = "TopX")] 
         public string TopX {get; set;}
        [JsonProperty(PropertyName = "TopY")] 
         public string TopY {get; set;}
        [JsonProperty(PropertyName = "BottomX")] 
         public string BottomX {get; set;}
        [JsonProperty(PropertyName = "BottomY")] 
         public string BottomY {get; set;}
    }

    public class ListOfLabelledImages
    {
        [JsonProperty(PropertyName = "id")]
        public string id { get; set; }
        [JsonProperty(PropertyName = "LabelledImages")]
        public string[] LabelledImages { get; set; }
        [JsonProperty(PropertyName = "_self")]
        public string SelfLink { get; set; }
    }
}
