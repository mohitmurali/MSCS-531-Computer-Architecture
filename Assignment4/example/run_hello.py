from m5.objects import *

system = System()
system.clk_domain = SrcClockDomain(clock="1GHz", voltage_domain=VoltageDomain())

# Memory system
system.mem_mode = "timing"
system.mem_ranges = [AddrRange("512MiB")]
system.mem_ctrl = SimpleMemory(
    range=system.mem_ranges[0],
    latency="1ns",
    bandwidth="4GiB/s"
)

# CPU and caches
system.cpu = X86TimingSimpleCPU()

def create_cache():
    return Cache(
        size="32KiB",
        assoc=8,
        tag_latency=1,
        data_latency=1,
        response_latency=1,
        mshrs=10,
        tgts_per_mshr=20
    )

system.cpu.icache = create_cache()
system.cpu.dcache = create_cache()

# Memory bus connections
system.membus = SystemXBar()
system.cpu.icache_port = system.cpu.icache.cpu_side
system.cpu.dcache_port = system.cpu.dcache.cpu_side
system.cpu.icache.mem_side = system.membus.cpu_side_ports
system.cpu.dcache.mem_side = system.membus.cpu_side_ports
system.mem_ctrl.port = system.membus.mem_side_ports  # Correct connection direction

# Workload setup
process = Process()
process.cmd = ['tests/test-progs/hello/bin/x86/linux/hello']
system.cpu.workload = process
system.cpu.createThreads()
system.cpu.createInterruptController()

# Connect interrupt ports (no indexing needed for single-thread)
system.cpu.interrupts.int_requestor = system.membus.cpu_side_ports
system.membus.mem_side_ports = system.cpu.interrupts.pio

system.workload = SEWorkload.init_compatible(process.cmd[0])

# Simulation
root = Root(full_system=False, system=system)
m5.instantiate()
print("Simulation started")
exit_event = m5.simulate()
print(f"Exiting @ {m5.curTick()}: {exit_event.getCause()}")
