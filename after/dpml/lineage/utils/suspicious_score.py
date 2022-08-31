def compute_suspicious_score(fail_num, pass_num, total_fail, total_pass):
    fail_percent = 0
    pass_percent = 0
    if total_fail != 0:
        fail_percent = fail_num / total_fail
    if total_pass != 0:
        pass_percent = pass_num / total_pass
    if fail_percent + pass_percent == 0:
        return 0
    else:
        return fail_percent / (fail_percent + pass_percent) * 100