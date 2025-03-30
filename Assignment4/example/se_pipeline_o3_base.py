from m5.objects import *
import m5
import os

binary_path = "tests/test-progs/hello/bin/x86/linux/hello"
if not os.path.exists(binary_path):
    raise FileNotFoundError(f"Binary not found: {binary_path}")

system = System()
system.clk_domain = SrcClockDomain(clock="1GHz", voltage_domain=VoltageDomain(voltage="1V"))
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

system.cpu = DerivO3CPU()
system.cpu.numThreads = 1
system.cpu.fetchWidth = 1
system.cpu.decodeWidth = 1
system.cpu.issueWidth = 1
system.cpu.commitWidth = 1
system.cpu.branchPred = None  # No prediction for baseline
system.cpu.numPhysIntRegs = 128
system.cpu.numPhysFloatRegs = 128

system.membus = SystemXBar()
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

system.cpu.icache = Cache(size='32kB', assoc=2, tag_latency=1, data_latency=1, response_latency=1, mshrs=4)
system.cpu.dcache = Cache(size='32kB', assoc=2, tag_latency=1, data_latency=1, response_latency=1, mshrs=4)
system.cpu.icache.cpu_side = system.cpu.icache_port
system.cpu.dcache.cpu_side = system.cpu.dcache_port
system.cpu.icache.mem_side = system.membus.cpu_side_ports
system.cpu.dcache.mem_side = system.membus.cpu_side_ports

system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

system.workload = SEWorkload.init_compatible(binary_path)
process = Process()
process.cmd = [binary_path]
system.cpu.workload = process
system.cpu.createThreads()

root = Root(full_system=False, system=system)
m5.instantiate()

print("Starting basic pipeline simulation...")
exit_event = m5.simulate(1000000000)
print(f"Simulation exited: {exit_event.getCause()} at tick {m5.curTick()}")
m5.stats.dump()
print("Statistics dumped to pipeline_stats.txt")
