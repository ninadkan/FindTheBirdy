using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using WebObjectDetector.Dashboard.Models;
using WebObjectDetector.Data;

namespace WebObjectDetector.Controllers
{
    [Authorize]
    public class DashboardController : Controller
    {

        private CosmosDBWrapper _cosmosDbWrapper;

        public DashboardController(CosmosDBWrapper wrapper)
        {
            _cosmosDbWrapper = wrapper;
        }
        public IActionResult Index()
        {
            return View();
        }

        public IActionResult Actions()
        {
            return View();
        }

        public IActionResult Results()
        {
            return View();
        }

        public IActionResult PerformanceAndScale()
        {
            return View();
        }

        public IActionResult OperationsAndMonitor()
        {
            return View();
        }

        [HttpGet()]
        public async Task<IActionResult> OperationsList()
        {
            var openCVObjects = await _cosmosDbWrapper.GetOpencvOperationsAsync();
            return View("OperationsList", openCVObjects);
        }

        [HttpGet("OperationsCreate")]
        public IActionResult OperationsCreate()
        {
            var obj = new OpencvOperations() { };
            return View("OperationsCreate", obj);
        }

        [HttpPost("OperationsCreate")]
        public async Task<IActionResult> Create([FromForm] OpencvOperations obj)
        {
            return await PostAsync(obj);
        }

        ////[HttpGet("{id}")]
        //public async Task<IActionResult> GetAsync(string id)
        //{
        //    var obj = await _cosmosDbWrapper.GetOpencvOperationsAsync(id);
        //    return View("GetAsync", obj);
        //}

        [HttpGet("OperationsEdit")]
        public async Task<IActionResult> OperationsEdit(string id)
        {
            var obj = await _cosmosDbWrapper.GetOpencvOperationsAsync(id);
            return View("OperationsEdit", obj);
        }

        [HttpPost("OperationsEdit")]
        public async Task<IActionResult> OperationsEdit([FromForm] OpencvOperations obj)
        {
            //var obj = await _cosmosDbWrapper.GetOpencvOperationsAsync(id);
            //return View("EditAsync", obj);
            return await PostAsync(obj);
        }

        [HttpGet("OperationsDetails")]
        public async Task<IActionResult> OperationsDetails(string id)
        {
            var obj = await _cosmosDbWrapper.GetOpencvOperationsAsync(id);
            return View("OperationsDetails", obj);
        }


        [HttpGet("OperationsDelete")]
        public async Task<IActionResult> OperationsDelete(string id)
        {
            var obj = await _cosmosDbWrapper.GetOpencvOperationsAsync(id);
            return View("OperationsDelete", obj);
        }


        //[HttpPost("id")]
        public async Task<IActionResult> DeletePost(string id)
        {
            var obj = await _cosmosDbWrapper.DeleteOpencvOperationsAsync(id);
            return RedirectToAction("OperationsList");
        }

        //[HttpPost()]
        public async Task<IActionResult> PostAsync([FromForm] OpencvOperations obj)
        {
            await _cosmosDbWrapper.SaveOpencvOperationsAsync(obj);
            return RedirectToAction("OperationsList");
        }
    }
}