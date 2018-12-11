using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;

namespace WebAppObjDetector.Controllers
{
    public class DashboardController : Controller
    {
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
    }
}