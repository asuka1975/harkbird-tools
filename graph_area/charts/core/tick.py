def calc_tick_start(tick_range, tick):
    if tick_range[0] % tick == 0:
        return tick_range[0]
    if tick_range[0] < 0:
        return tick_range[0] - (tick_range[0] % -tick)
    else:
        return tick_range[0] + (tick - (tick_range[0] % tick))

def calc_num_ticks(tick_range, tick):
    num_ticks = (tick_range[1] - tick_range[0]) // tick
    if tick_range[0] % tick == 0 or tick_range[1] % tick == 0:
        num_ticks += 1
    return num_ticks