If anyone face the problem that the following command is not changing the "windows" to new the volume label "WIN", after mounting EFI volume :
sudo bless --folder /Volumes/EFI/EFI/Boot --label WIN

just replace the "label" by "file", that is ..

sudo bless --folder /Volumes/EFI/EFI/Boot/bootx64.efi --file WIN

or

sudo bless --folder /Volumes/EFI/EFI/Boot/bootx64.efi --file "WIN 10"

quotes are used in case your new label(WIN 10) contains spaces.

Related to Icon replacement it can be done easily by using old method without using any scripts or terminal command (for both Mac and windows volumes):

a. Use Finder preferences --> General ---> Show hard disk, to display your
volumes on desktop.

b. Select “Macintosh HD” Volume (MacOS volume) then use right click --> “Get Info”--> select the small hard disk image located in upper left corner.

c. Choose any icon, with an extension \*.icns and NOT Jpeg or PNG images, and drag it on the small image (step b), you will see that the desktop volume icon is automatically changed.

d. You can use “image2icon” application from apple store to convert your favourite images to icons (1024X1024 pixel) with an extension “.icns”.

If you installed "BigSur 11.1" from scratch or clean install, the account name chosen will be the macOS volume name displayed directly in boot start up
manager and no need for renaming.

So Easy !!!!!!!!
