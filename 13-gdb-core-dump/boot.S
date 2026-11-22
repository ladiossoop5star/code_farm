// SPDX-License-Identifier: MIT
.section .text.boot,"ax"
.global _start
_start:
    ldr x0, =stack_top
    mov sp, x0
    ldr x0, =vectors
    msr vbar_el1, x0
    isb
    bl main
1:  wfe
    b 1b

.align 11
vectors:
.rept 16
    b capture
    .balign 128
.endr

capture:
    sub sp, sp, #288
    stp x0, x1, [sp, #0]
    stp x2, x3, [sp, #16]
    stp x4, x5, [sp, #32]
    stp x6, x7, [sp, #48]
    stp x8, x9, [sp, #64]
    stp x10, x11, [sp, #80]
    stp x12, x13, [sp, #96]
    stp x14, x15, [sp, #112]
    stp x16, x17, [sp, #128]
    stp x18, x19, [sp, #144]
    stp x20, x21, [sp, #160]
    stp x22, x23, [sp, #176]
    stp x24, x25, [sp, #192]
    stp x26, x27, [sp, #208]
    stp x28, x29, [sp, #224]
    str x30, [sp, #240]
    add x0, sp, #288
    str x0, [sp, #248]
    mrs x0, elr_el1
    mrs x1, spsr_el1
    stp x0, x1, [sp, #256]
    mrs x0, esr_el1
    mrs x1, far_el1
    stp x0, x1, [sp, #272]
    mov x0, sp
    bl save_report
2:  wfe
    b 2b
