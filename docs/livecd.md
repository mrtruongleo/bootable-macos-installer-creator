This workaround worked on my 13" Apple Macbook Pro mid-2009 running 64-bit XUbuntu 20.04:

Create a LiveCD of the _Ubuntu (i.e. Ubuntu, XUbuntu, KUbuntu...) distribution just in case.
Delete the shim_.efi file located at /boot/efi/EFI/ubuntu/
Use APT to purge (i.e. completely uninstall) the shim DEB packages (shim and shim-signed) from the system.
Delete the grub folder located at /boot
Install GRUB again (i.e. perform a "fresh" or "clean" GRUB install with a command such as grub-install /dev/sda ; grub-install --recheck).
Fix GRUB's default settings at /etc/default/grub in order to [1] activate GRUB's console mode and [2] force GRUB to show its menu for 3 seconds, under such console mode. You do this by basically setting GRUB_TIMEOUT_STYLE=menu, GRUB_TIMEOUT=3 and GRUB_TERMINAL=console in /etc/default/grub.
Run sudo update-grub so these fixed default settings are applied to the "fresh" GRUB install.
Run efibootmgr in order to make sure that ubuntu (i.e. grubia32.efi or grubx64.efi, created and stored at /boot/efi/EFI/ubuntu) still is the default EFI boot loader option.
Reboot the system.
Boot from the LiveCD in case of problem.
(VERY) LONG ANSWER: HOW TO PERFORM THE ABOVE PROCEDURES

CREATE THE LIVECD.

There are several ways to create a LiveCD. The most basic ones, in my opinion, consist of downloading the \*Ubuntu LiveCD .iso file (e.g. ubuntu-20.04-amd64.iso) and then either using UNetbootin to burn it into a USB stick (flashdrive) or (if you have access to a Linux shell terminal such as bash) using dd to burn such .iso file into any external media (USB stick, writeable CD-ROM etc.). The answers to this question provide a quite detailed set of procedures about it.

DELETE THE SHIM EFI FILES.

Once you've created your LiveCD and tested it to make sure that it's going to work if you happen to need it, open a shell terminal emulation window (CtrlAltT is a shortcut to it, but you can also run it from the Applications panel/menu or right-click a free area in the Desktop and then select the Terminal option) and then run sudo su in the terminal so you become the root user. Becoming root will spare you from having to use sudo on every shell command from this point on. After becoming root, delete the shim\*.efi file (e.g. shimia32.efi for 32-bit systems, shimx64.efi for 64-bit systems) that is probably located at /boot/efi/EFI/ubuntu. Assuming that the shim .efi file is indeed located at /boot/efi/EFI/ubuntu, it can be deleted by running this command in the terminal:

rm /boot/efi/EFI/ubuntu/shim\*.efi
If the EFI partition isn't mounted, the command mount /boot/efi will likely mount it. If such command doesn't mount it, run lsblk -o NAME,FSTYPE,MOUNTPOINT,PARTLABEL |grep -i efi to find your EFI partition (e.g. /dev/sda1) and then mount it (e.g. mount /dev/sda1 /boot/efi). If the /boot/efi mount point does not exist, create it with the command mkdir -p /boot/efi and then mount the EFI partition at it (e.g. mount /dev/sda1 /boot/efi).

Furthermore, once such EFI partition is mounted at /boot/efi, and assuming that the shim .efi file is at /boot/efi/EFI/ubuntu, a command like thunar /boot/efi/EFI/ubuntu or nautilus /boot/efi/EFI/ubuntu (depending on which file manager your system uses) will give you root access to such folder (e.g. /boot/efi/EFI/ubuntu) directly from your file manager (windowed interface): this makes it easier to browse, find and then delete the shim .efi file (e.g. shimx64.efi).

_WARNING_ If you're connected as root and accidentally delete the wrong file, such file is lost forever (it does not go to the trash bin). It's therefore advised that you pay a lot of attention on what you're doing so you don't end up rendering your operating system unusable/inaccessible.

In case you're wondering why you should delete the shim .efi file (i.e. the 32-bit shimia32.efi file or the 64-bit shimx64.efi file): GRUB's .efi file (i.e. the 32-bit grubia32.efi file or the 64-bit grubx64.efi file) is the appropriate one to use on a computer where Secure Boot is disabled. The shim version actually just provides a signed version of the GRUB .efi file version (because Secure Boot requires such signed version). But if you install *Ubuntu on a Mac with disabled Secure Boot (which is the frequent case), *Ubuntu adds the shim EFI file as the default option even though the Mac's firmware tells the bootlader to load the unsecure GRUB EFI file. So the solution is to delete the shim (Secure Boot) EFI file and then make the GRUB (non-Secure Boot) EFI file the new default one that must "interact" with the Mac's hardware at boot time.

PURGE THE SHIM DEB PACKAGES.

After you delete the shim .efi file that was located at e.g. /boot/efi/EFI/ubuntu, run APT to purge the shim DEB packages and therefore prevent future shim updates from creating the problematic .efi file again:

apt-get purge shim shim-signed --allow-remove-essential -y
DELETE THE GRUB FOLDER.

Now that you're rid of shim, it's time to get rid of GRUB: go back to your file manager window (e.g. Nautilus, Thunar...) and delete the grub folder that is likely located at /boot. If you don't find the grub folder in /boot, run the command updatedb ; locate -i grubenv to find the location of the grubenv file: this file is stored at the grub folder, thus if you find the location of the grubenv file you find the location of the grub folder.

If you prefer to delete the grub folder from the terminal (assuming that it's located at /boot), just run:

rm -r /boot/grub
...and the grub folder will be deleted.

INSTALL A "FRESH" COPY OF GRUB.

Assuming that GRUB was installed in your first SATA storage drive (i.e. sda), install it back there by running this command:

grub-install /dev/sda ; grub-install --recheck
If your EFI partition is located at e.g. sda (e.g. /dev/sda1), it's common practice to install GRUB in /dev/sda. If your EFI partition is located at e.g. sdb (e.g. /dev/sdb1), it's common practice to install GRUB in /dev/sdb. And so on.

As explained here, it's also possible to use your LiveCD to install a "fresh" GRUB in your boot disk (e.g. /dev/sda). This method is particularly useful when your system's GRUB installer is damaged and you're temporarily unable to reinstall it through e.g. APT. I.e. for a 64-bit Intel Mac, the root installation command currently is apt install grub-common grub-efi grub-efi-amd64 grub-efi-amd64-bin grub-efi-amd64-signed grub-pc-bin grub2-common, but if it's not working on your system, you can always boot the LiveCD so GRUB is installed from the packages that are running from your LiveCD and then the new grub folder created in e.g. /boot is created by this LiveCD's GRUB.

FIX GRUB'S DEFAULT SETTINGS.

If you don't have the Gedit text editor, install it by running the command apt-get install gedit -y and then run this command in order to edit GRUB's default settings file with Gedit:

gedit /etc/default/grub
Once the Gedit window shows the contents of the grub file, remove the # character that is located at the left side of each one of the parameters GRUB_TIMEOUT_STYLE, GRUB_TIMEOUT and GRUB_TERMINAL, and then modify their options so they become these:

GRUB_TIMEOUT_STYLE=menu
GRUB_TIMEOUT=3
GRUB_TERMINAL=console
The menu option tells GRUB that it must create and show a menu when the computer is started or restarted.
The 3 option tells GRUB that it must wait 3 seconds before automatically booting the default operating system kernel, so the user has enough time to e.g. select a different kernel from the menu (if you prefer, you may either lower it to 1 or 2, or increase it to 4, 5 etc.).
The console option tells GRUB that it must ignore the graphics card's most appropriate driver and instead use a simplified VGA display driver that is much more basic but also much more compatible: it won't provide a fancy menu, but will provide a functional one that's more likely to work and be visible.
When you're done making the above modifications, save the file and then exit the Gedit text editor.

If you prefer to use the shell's standard text editor (which happens to be Nano), run nano /etc/default/grub instead of gedit /etc/default/grub.

APPLY THE CHANGES THAT WERE MADE IN GRUB'S DEFAULT SETTINGS.

This one is easy. Just go back to the terminal and run this command:

update-grub
The above command will read the content of /etc/default/grub and apply it into the settings of the "fresh" GRUB install, thus changing GRUB's behavior from this point on.

MAKE SURE THAT THE CORRECT BOOT EFI IS SELECTED.

Assuming that your EFI partition is mounted at /boot/efi and the shim .efi file that you deleted was stored at /boot/efi/EFI/ubuntu (this is \*Ubuntu's default location for its .efi files), check if the GRUB's .efi file is there:

ls -l /boot/efi/EFI/ubuntu/ |grep -i '.efi'
Because Intel Macs are 64-bit computers, it's expected that a 64-bit \*Ubuntu was installed on it, and that therefore a file named grubx64.efi is found by the command above. However, 32-bit systems should instead use a file named e.g. grubia32.efi, so in case your system is a 32-bit one, look for the 32-bit version of the GRUB .efi file.

If no GRUB .efi file is found, something's wrong and you're advised to install GRUB again (see STEP 5).

If the GRUB .efi file is found, then it's now time to check if the ubuntu EFI folder is selected as the default (i.e. first) source of .efi files (this precedence is important at boot time). In order to do it, run this command:

efibootmgr
The output must show something like this:

BootCurrent: 0001
BootOrder: 0001,0080
Boot0001* ubuntu
Boot0080* Mac OS X
Boot0081* Mac OS X
Boot0082*
BootFFFF*
In my case, ubuntu is identified as Boot0001* (its number is 0001), thus it's the one that needs to be the default option: from left to right, BootOrder must show 0001 (i.e. ubuntu) first. If this is not your case, fix it by running a command like this:

efibootmgr --bootorder 0001,0080,0081
This is going to make 0001 (i.e. ubuntu) the first boot option, 0080 (i.e. Mac OS X) the second one, and 0081 (i.e. Mac OS X) the third one (I'm yet to find what is the difference between 0080 and 0081. Anyway...).

If your bootloader is placed at e.g. /dev/sdb, you must update the boot manager by running the command efibootmgr --disk /dev/sdb.

If ubuntu isn't the active boot, make it active with efibootmgr -b 0001 -a. See more e.g. here or by running efibootmgr --help.

REBOOT THE SYSTEM.

Reboot your system in order to check if all this long journey fixed things out. You may reboot it from the menu or by running one of these terminal commands:

init 6
or

reboot
or

shutdown -r now
or

telinit 6
BOOT FROM THE LIVECD IN CASE OF PROBLEM.

The standard way to boot from a LiveCD on a Mac (iMac, Macbook etc.):

Power the Mac off.
Turn it on again and immediately hold the option key.
Type the password (if any was recorded in it) and hit enter.
Plug in your LiveCD USB stick, external DVD drive containing a LiveCD DVD, Mac's internal DVD drive containing a LiveCD etc. and wait.
Once the Mac reads the contents of the LiveCD, a new icon will show up on the screen. Select it with the arrow keys (◀ and ▶) and hit enter (i.e. return).
From here there are many possibilities depending on what went wrong. You may e.g. want to use your LiveCD to reinstall and/or update GRUB. In the worst case scenario, you can use the LiveCD to backup your data (to e.g. an external drive) and then reinstall the \*Ubuntu distribution.
