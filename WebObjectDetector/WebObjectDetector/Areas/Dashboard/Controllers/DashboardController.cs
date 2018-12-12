using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace WebObjectDetector.Areas.Dashboard.Controllers
{
    [Authorize]
    [Area("Dashboard")]
    public class DashboardController : Controller
    {
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
    }
}