sudo grub-install --target=x86_64-efi --efi-directory=/Volumes/GrubPartition --boot-directory=/Volumes/GrubPartition/boot /dev/disk0
mkdir /Volumes/GrubPartition/boot/grub
nano /Volumes/GrubPartition/boot/grub/grub.cfg

#
set timeout=5

menuentry 'Boot Windows Installer' {
    set root=(hd0,gpt2)  # Adjust based on your partition layout
    linux /Windows\ installer/Windows10_22H2.iso
    initrd /Windows\ installer/Windows11_24H2.iso
    boot
}

menuentry 'Boot Linux' {
    set root=(hd0,gpt3)  # Adjust based on your Linux partition
    linux /vmlinuz root=/dev/disk0s3
    initrd /initrd.img
    boot
}
