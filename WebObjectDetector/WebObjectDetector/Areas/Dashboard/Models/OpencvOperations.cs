using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Newtonsoft.Json; 

namespace WebObjectDetector.Areas.Dashboard.Models
{
    public class OpencvOperations
    {
        [JsonProperty(PropertyName = "id")]
        public string Id { get; set; }

        [JsonProperty(PropertyName = "MessageId")]
        public string MessageId { get; set; }

        [JsonProperty(PropertyName = "ExperimentName")]
        public string ExperimentName { get; set; }

        [JsonProperty(PropertyName = "Offset_Value")]
        public int Offset_Value { get; set; }

        [JsonProperty(PropertyName = "CurrentCount")]
        public int CurrentCount { get; set; }

        [JsonProperty(PropertyName = "MaxItems")]
        public int MaxItems { get; set; }

        [JsonProperty(PropertyName = "Time")]
        public float Time { get; set; }

        [JsonProperty(PropertyName = "Status")]
        public string Status { get; set; }
    }
}
