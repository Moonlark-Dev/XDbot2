from .monomer import Monomer
from .contingent import Contingent
from .scheduler import Scheduler

def init_debug():
    active = Contingent([Monomer("ice_king", {}, "ice_king", 100)])
    passive = Contingent([Monomer("ice_king", {}, "ice_king", 100)])
    active.enemy = passive
    passive.enemy = active
    scheduler = Scheduler(active, passive)
    scheduler.start_fighting()
    print("Done")