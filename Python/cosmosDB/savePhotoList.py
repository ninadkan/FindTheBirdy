import datetime
from  cosmosDBWrapper import clsCosmosWrapper

DataClassification_Good = [ 
                '2018-04-15_0638',
                '2018-04-15_0639',
                '2018-04-15_0654', 
                '2018-04-15_0803',
                '2018-04-15_0845',
                '2018-04-15_0853',
                '2018-04-15_0854',
                '2018-04-15_0855',
                '2018-04-16_0405',
                '2018-04-16_0406',
                '2018-04-16_0453',
                '2018-04-16_0731',
                '2018-04-16_0746',
                '2018-04-16_0751',
                '2018-04-16_1002',
                '2018-04-16_1003',
                '2018-04-16_1004',
                '2018-04-21_0808',
                '2018-04-21_0809',
                '2018-04-21_0911',
                '2018-04-21_0914',
                ]

clsObj = clsCosmosWrapper()
#clsObj.saveGoodPhotoListToCosmosDB(DataClassification_Good)

experiments = ['BirdImageDetection-2018-11-06 16:48:18.084983', 'BirdImageDetection-2018-11-06 17:06:13.968824']

for exp in experiments:
    goodImages = clsObj.returnGoodPhotoList(exp)
    for images in goodImages:
        print(images)

    