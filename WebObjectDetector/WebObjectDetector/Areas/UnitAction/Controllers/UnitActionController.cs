using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace WebObjectDetector.Areas.UnitAction.Controllers
{
    [Authorize]
    [Area("UnitAction")]
    public class UnitActionController : Controller
    {
        public IActionResult Index()
        {
            //var items = CosmosDbWrapper.GetCollection();


            //if (items != null && items.Count > 0)
            //{
            //    List<SelectListItem> expColl = items.Select(x => new SelectListItem() { Text = x.Id, Value = x.SelfLink }).ToList();
            //    SelectList selList = new SelectList(expColl, "Value", "Text");
            //    ViewBag.ExperimentCollectionVB = selList;
            //    return View("SinglePageView");
            //}
            //return View();
            return View();
        }


        public IActionResult CopyFilesAndCreateExperiment()
        {
            return View();
        }


        public IActionResult CreateViewUpdateMask()
        {
            return View();
        }


        public IActionResult SelectExperimentAndLabelImages()
        {
            return View();
        }


        public IActionResult DisplayAndLabelSelectedImages()
        {
            return View();
        }


        public IActionResult ImageMaskTag()
        {
            return View();
        }


        public IActionResult SinglePageView()
        {
            return View();
        }






    }
}