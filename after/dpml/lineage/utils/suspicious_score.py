def compute_suspicious_score(fail_num, pass_num, total_fail, total_pass):
    fail_percent = fail_num / total_fail
    pass_percent = pass_num / total_pass
    return fail_percent / (fail_percent + pass_percent) * 100