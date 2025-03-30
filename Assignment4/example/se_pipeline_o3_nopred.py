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

# CPU setup: Out-of-Order (DerivO3CPU)
system.cpu = DerivO3CPU()

# Configure pipeline width (single-issue baseline)
system.cpu.fetchWidth = 1
system.cpu.decodeWidth = 1
system.cpu.issueWidth = 1
system.cpu.commitWidth = 1

# ignore branch prediction
# system.cpu.branchPred = LocalBP()  # Basic local branch predictor

# Configure physical register files
system.cpu.numPhysIntRegs = 128
system.cpu.numPhysFloatRegs = 128

# Enable Simultaneous Multithreading (SMT) - 1 thread
system.cpu.numThreads = 1

# Memory bus setup
system.membus = SystemXBar()

# Interrupt controller setup
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# Cache setup with MSHRs
system.cpu.icache = Cache(
    size='32kB',
    assoc=2,
    tag_latency=1,
    data_latency=1,
    response_latency=1,
    mshrs=8,  # Set MSHRs for icache
    tgts_per_mshr=16
)

system.cpu.dcache = Cache(
    size='32kB',
    assoc=2,
    tag_latency=1,
    data_latency=1,
    response_latency=1,
    mshrs=8,  # Set MSHRs for dcache
    tgts_per_mshr=16
)

# Connecting cache to CPU
system.cpu.icache.cpu_side = system.cpu.icache_port
system.cpu.dcache.cpu_side = system.cpu.dcache_port
system.cpu.icache.mem_side = system.membus.cpu_side_ports
system.cpu.dcache.mem_side = system.membus.cpu_side_ports

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
system.cpu.createThreads()  # Enable threading

# Simulation setup
root = Root(full_system=False, system=system)
m5.instantiate()

# Run Simulation
print("Starting simulation with DerivO3CPU...")
exit_event = m5.simulate(1000000000)  # Run up to 1 billion ticks
print(f"Simulation exited: {exit_event.getCause()} at tick {m5.curTick()}")

# Dump statistics
m5.stats.dump()
print("Statistics dumped to pipeline_stats.txt")
