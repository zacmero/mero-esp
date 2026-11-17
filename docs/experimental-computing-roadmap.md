# Experimental computing roadmap for Mero ESP

Recorded: **2026-11-17 (America/Sao_Paulo)**. Based on the board investigation of 2026-11-16 and the subsequent experiment discussion.

## Purpose and status

Preserve the directions that make this board interesting as a small computer: operating systems, emulated processors, interactive programming environments, independent coprocessor execution, and a standalone generative instrument.

**This is a research and experiment plan. None of the new operating systems, emulators, language environments, ULP experiments, or A2DP applications below has been validated on this particular board.** Upstream implementations and this repository's hardware evidence support the feasibility assessments. An upstream demonstration on another board is identified as such.

The recorded hardware session ended with the original ESP-AT firmware restored and its full flash readback matching the original backup. These directions generally use alternative firmware builds; they are not applications to install into the restored AT firmware. See the [board report](../README.md), [progress record](../progress.md), and [probe/recovery commands](probe-commands.md). Saving this roadmap does not change that recorded board state.

## 1. Hardware baseline

| Resource | Evidence and planning consequence |
| --- | --- |
| Chip | ESP32-D0WD-V3, revision v3.1: the original Xtensa ESP32 family. |
| Main CPU | Two Xtensa LX6 cores, up to 240 MHz. |
| Internal SRAM | Espressif specifies 520 KB for the chip; this is not a measurement of free application heap. Firmware, stacks, buffers and other allocations consume part of it. |
| Flash | 4,194,304 bytes read and verified: 4 MiB, displayed as 4 MB by esptool. This is nonvolatile storage, not an equivalent amount of working RAM. |
| PSRAM | No verified external PSRAM capacity in the board report. Select experiments that can start without it. |
| Module/carrier | The original firmware banner says WROOM-32. Exact physical module and carrier markings still need inspection. |
| Serial | Recorded as `/dev/ttyACM1`; prefer the established persistent device path when it still identifies the same board. `/dev/ttyACM0` was a different device. |
| Radios | Wi-Fi association/DHCP/DNS/HTTP, BLE GATT, and Classic SPP/RFCOMM passed the recorded functional tests. This does not establish A2DP audio operation. |
| Low-power processor | Original ESP32 ULP FSM coprocessor. The esptool “LP Core” wording does not mean a third full-speed Xtensa core or the RISC-V LP core of newer chips. |
| Current equipment assumption | Board and working USB connection. Additional headers, display, keyboard, SD adapter and PSRAM are not prerequisites for the first selected experiment. |

Sources: [local identification](evidence/flash-id.txt), [recorded restoration](evidence/restore-hashes.txt), [ESP32 datasheet](https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf), [Espressif ULP overview](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/system/ulp.html).

The working tool environment is already recorded in [requirements-tools.txt](../requirements-tools.txt). Reuse it rather than repeating the failed pacman installation. The USB bridge's DTR/RTS behavior needed special handling for MicroPython; [run_device.py](../scripts/run_device.py) preserves the workaround.

## 2. Candidate map

“No new parts” means the selected implementation can use the existing USB connection and onboard storage. It still requires building/configuring and installing suitable firmware.

| Direction | What executes on the ESP32 | Equipment beyond the board and USB | Assessment |
| --- | --- | --- | --- |
| CP/M retrocomputer | Z80/8080 emulation, guest OS and vintage programs | None for a serial/internal-flash configuration | First recommended project; build and board validation pending. |
| NuttX | Native embedded OS, shell, tasks, files and drivers | None for the initial serial configuration | Strong native OS direction. |
| NuttX + WebAssembly | Native OS hosting a small bytecode runtime and guest programs | Potentially none; memory budget must be measured | Second-stage extension after basic NuttX works. |
| ESP32forth | Resident Forth interpreter/compiler and personal vocabulary | None; browser access is optional | Strong live-programming candidate. |
| uLisp | Resident Lisp interpreter and saved workspace | None for the serial/internal-flash setup | Strong symbolic-computation alternative. |
| ULP experiment | Main CPU assembles code for the smaller physical coprocessor | None for a shared-memory counter | Short, distinctive architecture experiment. |
| Emulated Linux | RISC-V emulator running Linux | The demonstrated route needs microSD and its interface | Later experiment; original-ESP32 precedent exists. |
| Bluetooth synthesizer | Procedural audio generation and A2DP transmission | An existing compatible Bluetooth speaker/headphones | Strong artistic application; audio profile untested here. |
| KolibriOS | Would require an appropriate x86/PC environment | No established configuration for this board | Preserve as a compatibility question, not an immediate target. |

## 3. KolibriOS: why it is not a direct flash target

KolibriOS targets x86-compatible PCs with an i586-class processor. Its kernel and many drivers are written in x86 assembly. The current homepage specifies 12 MB RAM; the installation document lists 8 MB. Both exceed the ESP32's internal SRAM.

There are two independent obstacles:

1. **Instruction set:** Xtensa cannot directly execute the existing x86 binaries.
2. **Machine environment:** the guest expects more memory and PC-style hardware, including suitable display/input support.

A small disk image fitting into flash does not resolve the working-memory requirement. An emulator could provide another instruction set and virtual devices, but it would need an appropriate 32-bit x86 implementation and backing storage for the guest's memory. An 8086/186 PC XT emulator is not sufficient evidence of KolibriOS compatibility.

**Assessment:** no verified, ready-to-use KolibriOS path was found for this board as currently equipped. This is not a claim of theoretical impossibility; producing such a path would be a substantial emulator and memory-system project.

Sources:

- [KolibriOS homepage](https://www.kolibrios.org/en)
- [KolibriOS installation requirements](https://docs.kolibrios.org/html/eng/INSTALL.HTML)
- [Official KolibriOS repository](https://github.com/KolibriOS/kolibrios)
- [8086tiny architecture and limitations](https://github.lgb.hu/8086tiny/doc.html)

## 4. First recommendation: a CP/M computer over USB

### Experience

The ESP32 emulates a Z80 or Intel 8080 computer, boots CP/M, and executes vintage applications. The Arch terminal supplies the keyboard and text display; guest instructions execute on the ESP32.

The target is a persistent little computer with an `A>` prompt, virtual disks, applications, and programming tools. Later, editing and compiling a program inside the guest would make the board host an entire development workflow.

### Preferred implementation: jscrane/cpm80

[cpm80](https://github.com/jscrane/cpm80) already contains the relevant implementation choices:

- Original ESP32 support through its r65emu dependency.
- A generic configuration allocating 64 KiB of emulated RAM.
- Host serial display and keyboard paths.
- Disk storage selected from SD, SPIFFS or LittleFS.
- Machine checkpoint/restore, optional CPU debugging and speed reporting.

The internal-flash storage route already exists; it does not require inventing an SD replacement. The inspected CP/M 2.2 disk images are 256,256 bytes each. Select a small set and verify the resulting firmware/filesystem layout within the board's total flash.

Source-level evidence:

- [Generic ESP32 configuration](https://github.com/jscrane/r65emu/blob/master/src/hw/esp32-example.h): `RAM_SIZE=0x10000`, conditional display/keyboard selection, LittleFS default.
- [Emulator setup](https://github.com/jscrane/cpm80/blob/master/cpm80.ino): `USE_HOST_DISPLAY`, serial output, optional external RAM, guest execution.
- [Disk implementation](https://github.com/jscrane/cpm80/blob/master/flash_disk.cpp): flash-backed disk reads/writes and machine checkpoint storage.
- [CP/M 2.2 disk directory](https://github.com/jscrane/cpm80/tree/master/disks/cpm22).

### First milestone

1. Select the actual ESP32 target and serial input/output configuration. The generic upstream build can select a TFT; explicitly choose the host display/keyboard paths instead.
2. Build a small CP/M 2.2 setup using onboard flash for disk images.
3. Boot to `A>` over USB and run `DIR`.
4. Run a small guest application.
5. Create a file on a writable virtual disk.
6. Close/flush it, restart the board, and verify that it remains readable.

After that: add a suitable editor and compiler or BASIC environment; compile/run a small program in the guest; explore CPU debugging and checkpoint/restore. Confirm how the chosen serial terminal exposes emulator control keys before relying on function-key shortcuts.

No performance measurement has been made on this board. An emulator's configured target clock is not a measured execution rate.

### Alternative: serial Altair emulator with BDS C

[Al Williams' FabGL fork](https://github.com/wd5gnr/FabGL) provides a concrete alternative. Its Altair example uses a serial console, a 64 KiB guest, internal-flash fallback when SD is unavailable, embedded CP/M and BDS C disks, and writable virtual disks.

This is an older implementation with board-specific assumptions. Its TTGO user-button mapping and remaining VGA/PS2 initialization need review or removal for a clean serial-only build. Pin dependency/toolchain versions rather than blindly flashing the old sketch.

Sources: [Altair8800.ino](https://github.com/wd5gnr/FabGL/blob/master/examples/VGA/Altair8800/Altair8800.ino), [machine configuration](https://github.com/wd5gnr/FabGL/blob/master/examples/VGA/Altair8800/src/machine.h), [author's firsthand serial-console experiment](https://hackaday.com/2020/08/20/esp32-altair-emulator-gets-split-personality/).

### Proposed Mero extension

Add a virtual I/O interface or a guest command that forwards a small request from CP/M to an ESP32-side network function. A vintage executable could then communicate with Mero Protocol or the Askey lab.

This bridge is **our proposed development**, not an existing cpm80 feature. Implement and inspect guest-to-host requests explicitly; keep the initial milestone independent of network integration.

### Alternatives that need more work

- [RunCPM](https://github.com/MockbaTheBorg/RunCPM) supports ESP32 and a 64 KiB guest, but its Arduino setup uses SD/SdFat. A LittleFS route would require adaptation.
- [ESP32-Z80-Emulator](https://github.com/djbottrill/ESP32-Z80-Emulator) can load boot content from SPIFFS, but its documented CP/M disk controller uses SD. SPIFFS boot support alone is not proof of a no-SD CP/M configuration.

## 5. Native OS direction: Apache NuttX

### Experience

[NuttX](https://nuttx.apache.org/docs/latest/introduction/about.html) runs directly on the Xtensa processor. It provides an embedded OS with POSIX/Unix-style interfaces: tasks, scheduling, threads, filesystems, device interfaces and sockets.

It is an independent RTOS, not a Linux distribution. Desktop Linux executables do not transfer unchanged. Begin with native applications built for NuttX/ESP32, commonly included in the firmware image.

The [ESP32 board documentation](https://nuttx.apache.org/docs/latest/platforms/xtensa/esp32/boards/esp32-devkitc/index.html) includes serial-shell, Wi-Fi, flash-filesystem and dual-core configurations. Select settings for the actual module; some upstream default configurations name WROVER, so inspect their assumptions instead of assuming external RAM exists.

### First milestone

Build a minimal serial NSH configuration and inspect tasks, free memory and device nodes. These are previews of commands inside the installed NuttX environment, not commands for the currently restored ESP-AT firmware:

```text
nsh> ps
nsh> free
nsh> ls /dev
```

Then add a writable filesystem in onboard flash and verify file persistence. Add two small tasks, inspect their state, and turn one of our own native programs into a shell command. Introduce Wi-Fi/network shell access after the basic OS and memory measurements are stable.

The objective is a personal computing environment with inspectable tasks, persistent files and programs. NSH supports commands, scripting and built-in applications; the exact feature set is selected at build time.

Sources: [NuttShell](https://nuttx.apache.org/docs/latest/applications/nsh/index.html), [ESP32 NSH configuration](https://github.com/apache/nuttx/blob/master/boards/xtensa/esp32/esp32-devkitc/configs/nsh/defconfig), [Wi-Fi NSH configuration](https://github.com/apache/nuttx/blob/master/boards/xtensa/esp32/esp32-devkitc/configs/wifinsh/defconfig).

### Second stage: WebAssembly programs as files

The ESP32 documentation includes a WebAssembly Micro Runtime configuration, with modules stored in LittleFS and launched using `iwasm`.

The proposed workflow is:

1. Compile a deliberately small guest program on the host.
2. Transfer the module to the board's filesystem.
3. Launch it in the on-board runtime.
4. Unload the module, compare free memory, and replace the guest program without replacing the entire OS image.

Start with interpreted Wasm bytecode and one minimal module; measure runtime, stack, heap and guest linear-memory requirements. Do not assume an Xtensa JIT or compatibility with AOT modules built for a different architecture. Runtime isolation depends on its implementation and exposed host functions; it does not automatically provide desktop-style hardware-protected processes. The full upstream debug/network configuration is not a promise that every combination will fit this board. This is a second-stage experiment, not a prerequisite for NSH.

Sources: [ESP32 WAMR configuration](https://github.com/apache/nuttx/blob/master/boards/xtensa/esp32/esp32-devkitc/configs/wamr_wasi_debug/defconfig), [WAMR project](https://github.com/wasm-micro-runtime/wasm-micro-runtime).

## 6. Interactive language computer: ESP32forth

[ESP32forth](https://esp32forth.appspot.com/ESP32forth.html) documents an original ESP32-WROOM configuration with 4 MB flash and PSRAM disabled. It offers a resident Forth interpreter/compiler, serial interaction, files, an editor and a browser terminal.

A small example, to run inside an installed Forth environment:

```forth
: square dup * ;
12 square .
```

The first line defines `square`. `dup` duplicates the input and `*` multiplies the two copies; `;` ends the definition. The second line invokes it and prints 144.

Definitions can be added interactively without reflashing the entire firmware. A small C nucleus supports a system whose interpreter/compiler is substantially built in Forth. Do not describe ordinary word compilation as a verified native Xtensa JIT.

### First milestone

Boot to the serial prompt, define and inspect a word, redefine it and compare the behavior, then save a small program/workspace using the project's supported persistence mechanism, restart and restore it. Then add an editor or browser terminal and a personal vocabulary of commands.

The board executes the language; the browser, when used, is its interface. Saved dictionary images should be treated as tied to a compatible firmware build.

The documentation mixes current release guidance with older board-table versions. Verify the chosen release and Arduino/toolchain combination before turning this into an installation recipe.

Sources: [ESP32forth manual](https://esp32forth.appspot.com/ESP32forth.html), [µEforth internals](https://eforth.appspot.com/internals.html), [upstream source](https://github.com/flagxor/ueforth).

## 7. Symbolic computer: uLisp

[uLisp for ESP32](https://github.com/technoblogy/ulisp-esp) provides a resident Lisp environment. The inspected source has an original ESP32/LX6 configuration without PSRAM, an internal-memory workspace and LittleFS support. A serial-first setup does not need the optional display or SD facilities.

A preview inside the installed interpreter:

```lisp
(defun square (x) (* x x))
(square 12)
(eval (list '+ 20 22))
(save-image)
```

The first call returns 144. The generated expression evaluates to 42. Saving an image preserves the Lisp workspace; it is not a snapshot of every hardware peripheral or CPU instruction.

### First milestone

Define functions, build and evaluate an expression as data, save the workspace, restart and load it again. A fitting follow-up is a small expression interpreter implemented in Lisp, connecting this device to the Coding Lab's evaluator/AST work.

A symbolic rule engine is another possible application. This is a small Lisp implementation, not desktop Common Lisp or a local large language model.

Sources: [project README](https://github.com/technoblogy/ulisp-esp), [ESP32 board and filesystem implementation](https://github.com/technoblogy/ulisp-esp/blob/master/ulisp-esp.ino).

## 8. A processor programming another processor: ULP

The original ESP32's ULP FSM is a small physical coprocessor able to execute limited programs while the main CPU sleeps. It can also wake the main CPU under configured conditions.

The [MicroPython ULP toolchain](https://github.com/micropython/micropython-esp32-ulp) assembles ULP machine code using MicroPython on the ESP32 itself. Its documentation records tests on original ESP32 hardware without SPIRAM.

The experiment therefore has two distinct execution environments: the main CPU runs Python and an assembler; the smaller ULP runs the resulting machine code and exchanges data through RTC memory.

### First milestone and extension

1. Run the upstream [counter example](https://github.com/micropython/micropython-esp32-ulp/blob/master/examples/counter.py).
2. Observe the ULP incrementing a shared value and the main CPU reading it.
3. Inspect the small assembly program and alter its behavior.
4. As a separate extension, put the main CPU into deep sleep while the ULP continues periodic work.
5. Wake the main CPU and inspect the retained result; later let the ULP trigger that wake at a threshold.

The existing counter example keeps the main CPU awake. The sleep demonstration is work to add, not an upstream result to claim from that example.

No external sensor is needed for shared-memory arithmetic. The ULP is suited to counters, comparisons and simple control, not a full guest OS or normal Wi-Fi/Bluetooth services while the main CPU sleeps. Do not infer whole-development-board power consumption from the coprocessor's low-power design.

Implementation note: `set_wakeup_period` uses microseconds. Follow the API documentation rather than the counter example's older comment describing the value as cycles.

Sources: [ULP toolchain documentation and tested hardware](https://github.com/micropython/micropython-esp32-ulp/blob/master/docs/index.rst), [Espressif ULP overview](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/system/ulp.html), [MicroPython esp32 API](https://docs.micropython.org/en/latest/library/esp32.html).

## 9. Later experiment: Linux through a RISC-V machine

[linux_on_m5stack](https://github.com/verylowfreq/linux_on_m5stack) demonstrates Linux on an original Xtensa ESP32 with 520 KB SRAM and no PSRAM.

Its emulated RV32IMA machine has 16 MB of guest memory backed by a microSD file. The ESP32 caches 224 blocks of 1,024 bytes in SRAM. Cache misses require card access, which makes execution very slow.

The author reports about eight minutes to boot Linux and about another minute to reach the shell. Input can use serial. These are the author's demonstration figures, not performance measured on this board.

### Requirements and first milestone

This route needs a microSD card/interface and adaptation of the M5Stack-specific display/button/startup code. Preserve it for when those parts are available.

First success: a serial Linux boot log, a shell and execution of a simple command. Record actual boot time, memory backing and card behavior. This is a study of CPU emulation and memory virtualization, not a proposed replacement for the lab's normal Linux machines.

Source: [implementation and memory notes](https://github.com/verylowfreq/linux_on_m5stack#linux-on-m5stack).

## 10. Artistic direction: standalone Bluetooth synthesizer

Use the original ESP32 as an **A2DP audio source**: generate audio samples on the board and transmit them to an existing Bluetooth speaker or headphones.

[ESP32-A2DP](https://github.com/pschatzmann/ESP32-A2DP/wiki/A2DP-Source) supports providing generated PCM samples through callbacks. The speaker handles the physical audio output; this source arrangement does not need an external DAC on the ESP32.

### First milestone

Generate a controlled test tone, connect to the intended Bluetooth audio device and verify sustained playback. Then replace the tone with a simple procedural voice or sequencer and control parameters over serial.

Possible I/O Experiments directions:

- Evolving drones.
- Rule-based melodic patterns.
- Slowly changing rhythms.
- A soundscape whose synthesis rules can be adjusted while it runs.

Audio generation executes on the ESP32. USB can supply power after installation, while the speaker receives audio wirelessly.

The recorded SPP/RFCOMM test establishes a different Bluetooth profile; A2DP remains untested here. Keep synthesis callbacks fast and nonblocking, and measure audio reliability before combining it with additional radio work. Start with generated/sequenced playback; latency for live instrument response would need separate measurement.

Sources: [supported hardware](https://github.com/pschatzmann/ESP32-A2DP/wiki/Supported-Hardware), [providing audio data](https://github.com/pschatzmann/ESP32-A2DP/wiki/Providing-Audio-Data), [library](https://github.com/pschatzmann/ESP32-A2DP).

## 11. Related leads to retain

These were research leads, not selected first builds.

| Lead | Reason to revisit / present limitation |
| --- | --- |
| [ESP32TinyFake86](https://github.com/rpsubc8/ESP32TinyFake86/blob/main/readmeEnglish.md) | Original-ESP32 DOS-era emulation without PSRAM is documented, but the inspected implementation uses VGA and PS/2. A USB-only interface would be additional work. |
| [FabGL PCEmulator](https://github.com/fdivitto/FabGL/blob/master/examples/VGA/PCEmulator/PCEmulator.ino) | The standard PC emulator expects physical PSRAM and SD storage. Disabling automatic PSRAM initialization in a build setting does not eliminate that hardware requirement. |
| [FUZIX](https://github.com/EtchedPixels/FUZIX) | Native ESP32 and emulated routes are research possibilities, but storage/configuration work remains. The bundled cpm80 FUZIX disk pair exceeds this board's entire 4 MiB flash before emulator overhead. Do not equate cpm80's FUZIX support with a fitting image here. |
| [Uxn-ESP32](https://github.com/max22-/uxn-esp32) | A small virtual machine with an original ESP32 target, but its current interface assumes display/controller hardware. A serial or browser interface is a possible porting project. |
| [tiny386](https://github.com/hchunhui/tiny386) | Relevant to more capable x86 emulation, but its inspected ESP targets and memory assumptions differ from this original ESP32 board. Its demonstrations do not establish KolibriOS support here. |

## 12. Recommended order and evidence to keep

1. **CP/M over USB with flash-backed disks.** Boot, run a guest program and prove persistence. Then add a guest programming tool.
2. **NuttX serial environment.** Inspect tasks/memory, add persistent files and native applications. Consider WAMR only after measuring available resources.
3. **ULP counter and sleep extension.** A short hardware-architecture detour that needs no additional connections.
4. **Choose a language environment or the artistic application.** ESP32forth/uLisp for live programming; A2DP synthesis for I/O Experiments.
5. **Linux through emulation when SD hardware is available.** Keep KolibriOS and the other larger ports as exploratory leads.

For every completed experiment, record the upstream commit/release, selected board configuration, toolchain versions, flash layout, actual resource measurements, reproduced commands and observed result. Distinguish upstream evidence, proposed behavior and measurements on this board.

Use the established [firmware preservation and recovery workflow](probe-commands.md). Keep raw backups and credentials in their existing private/ignored locations. When a new image is left installed, update the board-state record so the original-firmware checkpoint is not mistaken for the current state.

The next concrete milestone remains: **an ESP32-hosted CP/M prompt, a program running inside the guest, and a file that survives a restart.**
