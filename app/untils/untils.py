# 检查时间跨度
def time_span_check(start_time, end_time, set_time_span):
    gap = (end_time - start_time).total_seconds()
    if gap > set_time_span * 24 * 3600:
        return True
    return False
