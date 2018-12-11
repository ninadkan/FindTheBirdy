﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;

namespace WebObjectDetector.Areas.Dashboard.Controllers
{
    [Area("Dashboard")]
    public class DashboardController : Controller
    {

        public IActionResult PendingActions()
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