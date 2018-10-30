#echo ---------- Creating Share  directory  -----------
#nadkmkdir Share
#echo ----------   Mounting Share  ---------
#sudo mount -t cifs //nkdsvm.file.core.windows.net/linuxraspshare/share /home/linuxuser/Share -o vers=3.0,username=nkdsvm,password=d19WRpMDg3zbG8FGFdHH0fXnVq52+IVBMMWTIivE/4/DBOoi++1nzqc9swHTenVGrwK24OmP0EUPiDmaZrFhEA==,dir_mode=0777,file_mode=0777,sec=ntlmssp
#echo ---------- Creating backup directory  ---------
#mkdir backup
echo ----------   Mounting Share  ---------
echo ----------   If the following command does not work,  have a look at the >>tail -f /var/log/kern.log
echo ----------   check that the share is accessible by using >>nmap nkdvsm.azure storage account.file.core.windows.net. The display should have 445/tcp open microsoft-ds ----------------
echo ----------   As last resort, just create the local folder in a shell and execute the mount command outside the shell script --------------
echo ----------   once done, you can unmount it with command >>sudo umount /home/ninadk/data
sudo mount -t cifs //nkdsvm.file.core.windows.net/experiment-findthebird/data /home/ninadk/BirdDetector/data -o vers=3.0,username=nkdsvm,password=d19WRpMDg3zbG8FGFdHH0fXnVq52+IVBMMWTIivE/4/DBOoi++1nzqc9swHTenVGrwK24OmP0EUPiDmaZrFhEA==,dir_mode=0777,file_mode=0777
#echo ----------- chaging the folder to Home folder ------------
#cd /home/linuxuser/Share
#DATE=$(date +"%Y-%m-%d_%H%M")
#echo ----------- copying the  jpg to stills.txt ------
#ls /home/linuxuser/Share/*.jpg > /home/linuxuser/Share/stills.txt
#mencoder -nosound -ovc lavc -lavcopts vcodec=mpeg4:aspect=16/9:vbitrate=8000000 -vf scale=1920:1080 -o /home/linuxuser/Share/$DATE-timelapse.avi -mf type=jpeg:fps=24 mf://@/home/linuxuser/Share/stills.txt
#echo -----------  moving the file  -----------
#mv -f /home/linuxuser/Share/*.jpg /home/linuxuser/backup
#echo -----------  zipping files --------------
#zip -r /home/linuxuser/backup/$Date.zip /home/linuxuser/backup/*.jpg
