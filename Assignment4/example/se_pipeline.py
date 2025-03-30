from m5.objects import *
import m5
import os

# Verify binary exists
binary_path = "tests/test-progs/hello/bin/x86/linux/hello"
if not os.path.exists(binary_path):
    raise FileNotFoundError(f"Binary not found: {binary_path}. Compile it with 'make' in tests/test-progs/hello/")

# System setup
system = System()
system.clk_domain = SrcClockDomain(clock="1GHz", voltage_domain=VoltageDomain(voltage="1V"))
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

# CPU and memory bus setup
system.cpu = TimingSimpleCPU()
system.membus = SystemXBar()

# Create and connect interrupt controller
system.cpu.createInterruptController()
# Connect interrupt controller ports to the memory bus
system.cpu.interrupts[0].pio = system.membus.mem_side_ports  # Programmed I/O port
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports  # Interrupt requestor port
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports  # Interrupt responder port

# Connect CPU cache ports
system.cpu.icache_port = system.membus.cpu_side_ports
system.cpu.dcache_port = system.membus.cpu_side_ports

# Memory setup
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# Workload setup
system.workload = SEWorkload.init_compatible(binary_path)
process = Process()
process.cmd = [binary_path]
system.cpu.workload = process
system.cpu.createThreads()  # Single thread

# Simulation setup
root = Root(full_system=False, system=system)
m5.instantiate()

# Simulate and dump stats
print("Starting simulation...")
exit_event = m5.simulate(1000000000)  # Run up to 1 billion ticks
print(f"Simulation exited: {exit_event.getCause()} at tick {m5.curTick()}")
m5.stats.dump()
print("Statistics dumped to pipeline_stats.txt")
