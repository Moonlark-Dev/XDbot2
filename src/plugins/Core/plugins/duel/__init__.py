from .monomer import Monomer
from .contingent import Contingent
from .scheduler import Scheduler


def init_debug():
    active = Contingent(
        [
            Monomer("ice_king", {}, "ice_king", 100, "Active_0"),
            # Monomer("ice_king", {}, "ice_king", 100, "Active_1"),
            # Monomer("scrorching_sun_phantom", {}, "scrorching_sun_phantom", 100, "Active_2"),
            Monomer("leather_case", {}, "leather_case", 100, "Acvive_1"),
        ]
    )
    passive = Contingent(
        [
            Monomer(
                "scrorching_sun_phantom", {}, "scrorching_sun_phantom", 100, "Passive_0"
            ),
            # Monomer("scrorching_sun_phantom", {}, "scrorching_sun_phantom", 100, "Passive_1"),
            # Monomer("leather_case", {}, "leather_case", 100, "Passive_2"),
            Monomer("ice_king", {}, "ice_king", 100, "Passive_1"),
        ]
    )
    active.enemy = passive
    passive.enemy = active
    scheduler = Scheduler(active, passive)
    scheduler.start_fighting()
    # print("Done")
