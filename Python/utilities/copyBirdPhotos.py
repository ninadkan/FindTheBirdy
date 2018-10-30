# Copy the files containing Birds to separate folder. 
import argparse
import os

# Following list contains all the photos which contain birds. 
# This list was compiled manually
BirdPhotos = ['2018-04-15_0638', 
              '2018-04-15_0639',
              '2018-04-15_0654', 
              '2018-04-15_0803',
              '2018-04-15_0845',
              '2018-04-15_0853',
              '2018-04-15_0854',
              '2018-04-15_0855',
              '2018-04-15_0916',
              '2018-04-16_0405',
              '2018-04-16_0406',
              '2018-04-16_0430',
              '2018-04-16_0446', 
              '2018-04-16_0447',
              '2018-04-16_0448',
              '2018-04-16_0449',
              '2018-04-16_0450',
              '2018-04-16_0453',
              '2018-04-16_0731',
              '2018-04-16_0746',
              '2018-04-16_0747',
              '2018-04-16_0749',
              '2018-04-16_0750',
              '2018-04-16_0751',
              '2018-04-16_0752',
              '2018-04-16_0753',
              '2018-04-16_0914',
              '2018-04-16_1002',
              '2018-04-16_1003',
              '2018-04-16_1004',
              '2018-04-16_1005',
              '2018-04-16_1007',
              '2018-04-16_1008',
              '2018-04-16_1009',
              '2018-04-16_1052',
              '2018-04-21_0808',
              '2018-04-21_0809',
              '2018-04-21_0827',
              '2018-04-21_0911',
              '2018-04-21_0914',
              '2018-04-21_0941',
              '2018-04-21_0942',
              '2018-04-21_0943',
              '2018-04-22_0233',
                         ]

def CpSrcDest(  IMGFOLDER = '..\\Data\\',
                EXTENSION = ".jpg",
                DESTINATION_FOLDER='..\\Data\\AllBirds\\'):
        """Copy files from source folder to destination folder
        [CpSrcDest]
        IMGFOLDER : Image folder location
        EXTENSION : extensions of the file that needs to be copied
        DESTINATION_FOLDER : location where the file needs to be copied
        """
        for i, imag in enumerate(BirdPhotos):
                filename= IMGFOLDER+ imag + EXTENSION
                cpCommand = "copy " + filename +  " " + DESTINATION_FOLDER
                os.system(cpCommand)
        return 

if __name__ == "__main__":
        parser = argparse.ArgumentParser(description=__doc__,
                        formatter_class=argparse.RawDescriptionHelpFormatter,)
        subparsers = parser.add_subparsers(dest="command")
        process_parser = subparsers.add_parser("CpSrcDest", help=CpSrcDest.__doc__)
        process_parser.add_argument("IMGFOLDER", nargs='?', default='..\\Data\\', help="Source Folder")
        process_parser.add_argument("EXTENSION", nargs='?',default='.jpg', help="file extension that needs to be copied")
        process_parser.add_argument("DESTINATION_FOLDER", nargs='?', default='..\\Data\\AllBirds\\', help="Destination Folder")
       
        args = parser.parse_args()
        if args.command == "CpSrcDest":
                CpSrcDest(args.IMGFOLDER, args.EXTENSION, args.DESTINATION_FOLDER)
        