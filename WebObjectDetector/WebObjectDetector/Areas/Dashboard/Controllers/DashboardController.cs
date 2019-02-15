using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using WebObjectDetector.Areas.Dashboard.Models;
using WebObjectDetector.Data;

namespace WebObjectDetector.Areas.Dashboard.Controllers
{
    [Authorize]
    [Area("Dashboard")]
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

        //[HttpGet()]
        public async Task<IActionResult> IndexAsync()
        {
            var openCVObjects = await _cosmosDbWrapper.GetOpencvOperationsAsync();
            Console.WriteLine("Length of Record = " + openCVObjects.Count.ToString()); 
            return View("IndexAsync", openCVObjects);
        }

        //[HttpGet("Create")]
        public IActionResult Create()
        {
            var obj = new OpencvOperations() { };
            return View("Create", obj);
        }

        //[HttpGet("{id}")]
        public async Task<IActionResult> GetAsync(string id)
        {
            var obj = await _cosmosDbWrapper.GetOpencvOperationsAsync(id);
            return View("GetAsync", obj);
        }

        //[HttpPost()]
        public async Task<IActionResult> PostAsync([FromForm] OpencvOperations obj)
        {
            await _cosmosDbWrapper.SaveOpencvOperationsAsync(obj);
            return RedirectToAction("IndexAsync");
        }
    }
}