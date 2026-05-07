from schedulers import EDF, LLF, RM

def main():
    rm_control = RM(10000, "rm_control")
    llf_control = LLF(10000, "llf_control")
    edf_control = EDF(10000, "edf_control")

    rm_resource_limiting = RM(10000, "rm_limiting", True)
    llf_resource_limiting = LLF(10000, "llf_limiting", True)
    edf_resource_limiting = EDF(10000, "edf_limiting", True)

    rm_overruns = RM(10000, "rm_overruns")
    rm_overruns.add_overruns(2000, 10, 5)
    llf_overruns = LLF(10000, "llf_overruns")
    llf_overruns.add_overruns(2000, 10, 5)
    edf_overruns = EDF(10000, "edf_overruns")
    edf_overruns.add_overruns(2000, 10, 5)

    simulations = [rm_control, llf_control, edf_control,
                   rm_resource_limiting, llf_resource_limiting, edf_resource_limiting,
                   rm_overruns, llf_overruns, edf_overruns]
    
    for simulation in simulations:
        simulation.add_task("Task-1", 13, 1, 4, 8)
        simulation.add_task("Task-2", 23, 7, 7, 17)
        simulation.add_task("Task-3", 29, 11, 9, 37)

        simulation.run()

if __name__ == "__main__":
    main()