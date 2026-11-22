/* SPDX-License-Identifier: MIT */
ENTRY(_start)
PHDRS
{
    text PT_LOAD FLAGS(5);
    ram PT_LOAD FLAGS(6);
}
SECTIONS
{
    . = 0x40080000;
    .text : { *(.text.boot) *(.text*) } :text
    .rodata : { *(.rodata*) } :text
    .note.gnu.build-id : { *(.note.gnu.build-id) } :text
    . = 0x400c0000;
    .ram (NOLOAD) : {
        crash_record = .;
        . += 0x1000;
        *(.bss*) *(COMMON)
    } :ram
    stack_top = 0x400c8000;
    /DISCARD/ : { *(.eh_frame*) *(.comment*) }
}
