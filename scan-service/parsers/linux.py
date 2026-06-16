# parsers/linux.py
# 주요정보통신기반시설 기술적 취약점 분석·평가 방법 상세가이드 (2026) 기준

def parse_result_file(content: str) -> dict:
    results = {}
    for line in content.strip().split("\n"):
        line = line.strip()
        if not line or "|" not in line:
            continue
        if line.startswith(("SCAN_DATE","HOSTNAME","OS","KERNEL","IP","===")):
            continue
        code, _, value = line.partition("|")
        code = code.strip()
        if code:
            results[code] = value.strip()
    return results


def judge_result(code: str, value: str) -> dict:
    if not value or value in ("NOT_FOUND", "UNKNOWN"):
        return {"result": "PENDING", "improvement": "수집된 데이터가 없어 수동 확인이 필요합니다."}

    judges = {
        "U-01": _u01, "U-02": _u02, "U-03": _u03, "U-04": _u04,
        "U-05": _u05, "U-06": _u06,
        "U-07": _u07_pending, "U-08": _u08_pending,
        "U-09": _u09, "U-10": _u10,
        "U-11": _u11_pending, "U-12": _u12, "U-13": _u13,
        "U-14": _u14, "U-15": _u15,
        "U-16": _file_perm_644, "U-17": _u17, "U-18": _shadow_perm,
        "U-19": _file_perm_644, "U-20": _u20, "U-21": _u21,
        "U-22": _file_perm_644,
        "U-23": _u23_pending, "U-24": _u24_pending,
        "U-25": _u25, "U-26": _u26,
        "U-27": _u27, "U-28": _u28, "U-29": _u29, "U-30": _u30,
        "U-31": _u31_pending, "U-32": _u32, "U-33": _u33_pending,
        "U-34": _svc_not_running, "U-35": _u35,
        "U-36": _svc_not_running, "U-37": _u37,
        "U-38": _svc_not_running, "U-39": _u39, "U-40": _u40,
        "U-41": _svc_not_running, "U-42": _svc_not_running,
        "U-43": _svc_not_running, "U-44": _svc_not_running,
        "U-45": _u45, "U-46": _u46, "U-47": _u47, "U-48": _u48,
        "U-49": _u49, "U-50": _u50, "U-51": _u51, "U-52": _u52,
        "U-53": _u53, "U-54": _u54, "U-55": _u55,
        "U-56": _u56, "U-57": _u57,
        "U-58": _u58, "U-59": _u59, "U-60": _u60, "U-61": _u61,
        "U-62": _u62, "U-63": _u63,
        "U-64": _u64_pending,
        "U-65": _u65, "U-66": _u66, "U-67": _u67,
    }
    fn = judges.get(code)
    return fn(value) if fn else {"result": "PENDING", "improvement": ""}


def _get(value, key):
    if f"{key}=" not in value:
        return ""
    part = value.split(f"{key}=")[1]
    return part.split()[0].strip() if part.split() else ""

def _not_running(v):
    return not v or "NOT_RUNNING" in v

def _perm_lsval_ok(ls_str, max_perm):
    pm = {"---":0,"--x":1,"-w-":2,"-wx":3,"r--":4,"r-x":5,"rw-":6,"rwx":7}
    s = ls_str.lstrip("-")[:9]
    if len(s) < 9:
        return False
    try:
        num = pm.get(s[0:3],9)*100 + pm.get(s[3:6],9)*10 + pm.get(s[6:9],9)
        return num <= max_perm
    except Exception:
        return False

def _u01(v):
    sshd = _get(v, "SSHD").lower()
    if sshd in ("no", "prohibit-password", "forced-commands-only"):
        return {"result": "Y", "improvement": ""}
    if sshd in ("yes", ""):
        return {"result": "N", "improvement": "/etc/ssh/sshd_config에서 PermitRootLogin no로 설정하세요."}
    return {"result": "PENDING", "improvement": "PermitRootLogin 설정을 수동으로 확인하세요."}

def _u02(v):
    conf = v.split("CONF=")[1] if "CONF=" in v else ""
    if not conf or "NOT_FOUND" in conf or "NOT_SET" in conf:
        return {"result": "N", "improvement": "/etc/security/pwquality.conf에서 minlen=8 이상, dcredit/ucredit/lcredit/ocredit=-1을 설정하세요."}
    try:
        minlen_tok = [p for p in conf.split() if "minlen" in p][0]
        minlen = int(minlen_tok.split("=")[1])
    except Exception:
        minlen = 0
    has_credit = any(c in conf for c in ["dcredit","ucredit","lcredit","ocredit","minclass"])
    if minlen >= 8 and has_credit:
        return {"result": "Y", "improvement": ""}
    tips = []
    if minlen < 8:
        tips.append(f"minlen을 8 이상으로 설정하세요 (현재: {minlen}).")
    if not has_credit:
        tips.append("dcredit, ucredit, lcredit, ocredit 복잡성 조건을 설정하세요.")
    return {"result": "N", "improvement": " ".join(tips)}

def _u03(v):
    denies = []
    for part in v.split():
        if "deny=" in part:
            try:
                denies.append(int(part.split("deny=")[1].rstrip(";,")))
            except Exception:
                pass
    if not denies:
        return {"result": "N", "improvement": "/etc/pam.d/system-auth 및 password-auth에 pam_faillock.so deny=5 이하로 설정하세요."}
    if all(1 <= d <= 5 for d in denies):
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": f"계정 잠금 임계값({denies})을 5 이하로 설정하세요."}

def _u04(v):
    shadow_perm = _get(v, "SHADOW_PERM")
    encrypt = _get(v, "ENCRYPT")
    passwd_field = _get(v, "PASSWD_FIELD")
    if passwd_field and passwd_field != "x":
        return {"result": "N", "improvement": "shadow 패스워드를 사용하도록 설정하세요."}
    if "NOT_FOUND" in shadow_perm:
        return {"result": "N", "improvement": "/etc/shadow 파일이 존재하지 않습니다."}
    if any(enc in (encrypt + shadow_perm).upper() for enc in ("SHA512","SHA256","SHA-512","SHA-256")):
        return {"result": "Y", "improvement": ""}
    return {"result": "PENDING", "improvement": "/etc/login.defs의 ENCRYPT_METHOD를 SHA-512로 설정하세요."}

def _u05(v):
    if v.strip() in ("NONE",""):
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": f"UID 0인 불필요한 계정({v})을 삭제하거나 UID를 변경하세요."}

def _u06(v):
    perm_str = _get(v, "SU_PERM")
    grp = _get(v, "SU_GROUP")
    perm_ok = "---" in perm_str[-3:] if perm_str else False
    group_ok = bool(grp) and grp not in ("NONE","root","")
    if perm_ok and group_ok:
        return {"result": "Y", "improvement": ""}
    tips = []
    if not perm_ok:
        tips.append("/bin/su 권한을 4750 이하로 설정하세요.")
    if not group_ok:
        tips.append("su 사용 가능 그룹을 wheel 등 특정 그룹으로 제한하세요.")
    return {"result": "N", "improvement": " ".join(tips)}

def _u07_pending(v):
    return {"result": "PENDING", "improvement": "로그인 가능한 계정 목록을 확인하고 불필요한 계정을 삭제하세요."}

def _u08_pending(v):
    if v.strip() in ("NONE",""):
        return {"result": "Y", "improvement": ""}
    return {"result": "PENDING", "improvement": "관리자 그룹(GID=0) 구성원이 최소화되어 있는지 확인하세요."}

def _u09(v):
    if v.strip() in ("NONE",""):
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": f"계정이 없는 GID가 존재합니다: {v}. 불필요한 그룹을 제거하세요."}

def _u10(v):
    if v.strip() in ("NONE",""):
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": f"중복 UID가 존재합니다: {v}. 각 계정에 고유한 UID를 부여하세요."}

def _u11_pending(v):
    if v.strip() in ("NONE",""):
        return {"result": "Y", "improvement": ""}
    return {"result": "PENDING", "improvement": f"로그인이 불필요한 시스템 계정에 /sbin/nologin 쉘이 설정되어 있는지 확인하세요: {v}"}

def _u12(v):
    tmouts = []
    for part in v.replace("PROFILE=","").replace("BASHRC=","").replace("PROFILE_D=","").split():
        if "TMOUT=" in part:
            try:
                tmouts.append(int(part.split("TMOUT=")[1].rstrip(";")))
            except Exception:
                pass
    if "NOT_SET" in v and not tmouts:
        return {"result": "N", "improvement": "/etc/profile 또는 /etc/profile.d/에 TMOUT=600 이하로 설정하세요."}
    if tmouts and all(0 < t <= 600 for t in tmouts):
        return {"result": "Y", "improvement": ""}
    if tmouts:
        return {"result": "N", "improvement": f"Session Timeout({tmouts}초)을 600초 이하로 설정하세요."}
    return {"result": "N", "improvement": "/etc/profile에 TMOUT=600 이하로 설정하세요."}

def _u13(v):
    logindefs = _get(v, "LOGIN_DEFS").upper()
    shadow_algo = v.split("SHADOW_ALGO=")[1].strip() if "SHADOW_ALGO=" in v else ""
    safe_logindefs = any(enc in logindefs for enc in ("SHA512","SHA256","SHA-512","SHA-256"))
    unsafe_users = [p for p in shadow_algo.split() if ":1:" in p or ":2a:" in p]
    if safe_logindefs and not unsafe_users:
        return {"result": "Y", "improvement": ""}
    if unsafe_users:
        return {"result": "N", "improvement": f"MD5 등 취약한 알고리즘 계정이 있습니다: {unsafe_users}. SHA-512로 변경하고 비밀번호를 재설정하세요."}
    if not safe_logindefs:
        return {"result": "N", "improvement": "/etc/login.defs에서 ENCRYPT_METHOD SHA512로 설정하세요."}
    return {"result": "PENDING", "improvement": "비밀번호 암호화 알고리즘을 수동으로 확인하세요."}

def _u14(v):
    path = _get(v, "PATH")
    if not path or path in ("NOT_FOUND",""):
        return {"result": "PENDING", "improvement": "root PATH 환경변수를 수동으로 확인하세요."}
    if ":." in path or path.startswith(".") or "::" in path:
        return {"result": "N", "improvement": f"PATH({path})에서 '.' 또는 '::'를 제거하세요."}
    return {"result": "Y", "improvement": ""}

def _u15(v):
    if v.strip() in ("NONE",""):
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": f"소유자/그룹이 없는 파일/디렉터리가 있습니다: {v}. chown으로 적절한 소유자를 설정하세요."}

def _file_perm_644(v):
    if "NOT_FOUND" in v:
        return {"result": "N/A", "improvement": "해당 파일이 존재하지 않습니다."}
    parts = v.split()
    if len(parts) >= 2 and parts[1] == "root" and _perm_lsval_ok(parts[0], 644):
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": "파일 소유자를 root로, 권한을 644 이하로 설정하세요."}

def _u17(v):
    if "NOT_FOUND" in v:
        return {"result": "N/A", "improvement": "시스템 시작 스크립트 디렉터리를 찾을 수 없습니다."}
    bad = [tok for tok in v.split(";") if tok.strip() and len(tok.split()) >= 4 and "w" in tok.split()[0][7:9]]
    if bad:
        return {"result": "N", "improvement": f"시스템 시작 스크립트에 일반사용자 쓰기 권한이 있습니다. chmod o-w로 제거하세요."}
    return {"result": "Y", "improvement": ""}

def _shadow_perm(v):
    if "NOT_FOUND" in v:
        return {"result": "N", "improvement": "/etc/shadow 파일이 없습니다."}
    parts = v.split()
    if len(parts) >= 2 and parts[1] == "root":
        pm = {"---":0,"--x":1,"-w-":2,"-wx":3,"r--":4,"r-x":5,"rw-":6,"rwx":7}
        s = parts[0].lstrip("-")[:9]
        try:
            num = pm.get(s[0:3],9)*100 + pm.get(s[3:6],9)*10 + pm.get(s[6:9],9)
            if num <= 400:
                return {"result": "Y", "improvement": ""}
        except Exception:
            pass
    return {"result": "N", "improvement": "/etc/shadow 소유자를 root로, 권한을 400 이하로 설정하세요."}

def _u20(v):
    if "INETD=NOT_FOUND" in v and "XINETD=NOT_FOUND" in v and "XINETD_D=NOT_FOUND" in v:
        return {"result": "Y", "improvement": ""}
    return {"result": "PENDING", "improvement": "/etc/(x)inetd.conf 파일 소유자(root) 및 권한(600 이하)을 확인하세요."}

def _u21(v):
    for key in ["RSYSLOG", "SYSLOG"]:
        info = _get(v, key)
        if not info or "NOT_FOUND" in info:
            continue
        parts = info.split()
        if len(parts) >= 2 and parts[1] == "root" and _perm_lsval_ok(parts[0], 644):
            return {"result": "Y", "improvement": ""}
    if "RSYSLOG=NOT_FOUND" in v and "SYSLOG=NOT_FOUND" in v:
        return {"result": "N/A", "improvement": "syslog 설정 파일이 없습니다."}
    return {"result": "N", "improvement": "/etc/rsyslog.conf 소유자를 root로, 권한을 644 이하로 설정하세요."}

def _u23_pending(v):
    dangerous = _get(v, "DANGEROUS")
    if dangerous and dangerous != "NONE":
        return {"result": "N", "improvement": f"불필요한 SUID/SGID 파일이 존재합니다: {dangerous}. 제거하거나 권한을 변경하세요."}
    return {"result": "PENDING", "improvement": "SUID/SGID 파일 목록을 확인하고 불필요한 파일의 권한을 제거하세요."}

def _u24_pending(v):
    return {"result": "PENDING", "improvement": "사용자 환경변수 파일(.bash_profile, .bashrc 등)의 소유자와 권한(644 이하)을 확인하세요."}

def _u25(v):
    if v.strip() in ("NONE",""):
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": f"world writable 파일이 존재합니다: {v}. chmod o-w로 쓰기 권한을 제거하세요."}

def _u26(v):
    if v.strip() in ("NONE",""):
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": f"/dev에 일반 파일이 존재합니다: {v}. rootkit 여부를 확인하고 불필요하면 제거하세요."}

def _u27(v):
    equiv = _get(v, "HOSTS_EQUIV")
    rhosts = _get(v, "RHOSTS")
    xinetd = _get(v, "R_XINETD")
    if equiv == "NOT_FOUND" and rhosts == "NONE" and xinetd == "NOT_FOUND":
        return {"result": "Y", "improvement": ""}
    if rhosts and rhosts != "NONE":
        return {"result": "N", "improvement": f".rhosts 파일({rhosts})을 제거하세요."}
    return {"result": "PENDING", "improvement": "r계열 서비스 및 hosts.equiv 설정을 수동으로 확인하세요."}

def _u28(v):
    deny = v.split("HOSTS_DENY=")[1].split("HOSTS_ALLOW=")[0].strip() if "HOSTS_DENY=" in v else "EMPTY"
    if deny == "EMPTY":
        return {"result": "N", "improvement": "/etc/hosts.deny에 ALL:ALL 설정 후 /etc/hosts.allow에 허용 호스트를 설정하세요."}
    if "all" in deny.lower():
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": "/etc/hosts.deny에 ALL:ALL 설정이 필요합니다."}

def _u29(v):
    if "NOT_FOUND" in v:
        return {"result": "Y", "improvement": ""}
    parts = v.split()
    if len(parts) >= 2 and parts[1] == "root" and "w" not in parts[0][7:]:
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": "/etc/hosts.lpd 소유자를 root로, 일반사용자 쓰기 권한을 제거하세요."}

def _u30(v):
    umasks = []
    for part in v.split():
        if "CURRENT=" in part:
            try:
                umasks.append(int(part.replace("CURRENT=","").lstrip("0") or "0", 8))
            except Exception:
                pass
    if umasks:
        if all(u >= 0o022 for u in umasks):
            return {"result": "Y", "improvement": ""}
        return {"result": "N", "improvement": f"UMASK 값을 022 이상으로 설정하세요."}
    return {"result": "PENDING", "improvement": "UMASK 설정을 수동으로 확인하세요."}

def _u31_pending(v):
    if "NOT_FOUND" in v:
        return {"result": "PENDING", "improvement": "홈 디렉터리 소유자 및 권한을 수동으로 확인하세요."}
    bad = [tok for tok in v.split(";") if tok.strip() and len(tok.split()) >= 4 and "w" in tok.split()[0][7:8]]
    if bad:
        return {"result": "N", "improvement": "일반사용자 쓰기 권한이 부여된 홈 디렉터리가 있습니다. chmod o-w로 제거하세요."}
    return {"result": "Y", "improvement": ""}

def _u32(v):
    if v.strip() in ("NONE",""):
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": f"홈 디렉터리가 없는 쉘 할당 계정이 있습니다: {v}. 홈 디렉터리를 생성하거나 쉘을 nologin으로 변경하세요."}

def _u33_pending(v):
    files = _get(v, "HIDDEN_FILES")
    dirs  = _get(v, "HIDDEN_DIRS")
    if files == "NONE" and dirs == "NONE":
        return {"result": "Y", "improvement": ""}
    return {"result": "PENDING", "improvement": "숨겨진 파일/디렉터리가 존재합니다. 악성 파일 여부를 확인하고 불필요하면 제거하세요."}

def _svc_not_running(v):
    if _not_running(_get(v,"PROCESS")):
        xinetd = _get(v,"XINETD")
        if not xinetd or xinetd == "NOT_FOUND":
            return {"result": "Y", "improvement": ""}
    if _get(v,"STATUS") == "inactive" and _not_running(_get(v,"PROCESS")):
        return {"result": "Y", "improvement": ""}
    if not _not_running(_get(v,"PROCESS")):
        return {"result": "N", "improvement": "해당 서비스를 비활성화하세요."}
    return {"result": "Y", "improvement": ""}

def _u35(v):
    ftp_proc = _get(v, "FTP_PROC")
    if _not_running(ftp_proc):
        return {"result": "N/A", "improvement": "FTP 서비스가 비활성화되어 있습니다."}
    anon = v.split("ANON_FTP=")[1].split("PROFTPD=")[0].strip() if "ANON_FTP=" in v else "NOT_FOUND"
    if "NOT_FOUND" in anon:
        return {"result": "N", "improvement": "/etc/vsftpd.conf에서 anonymous_enable=NO로 설정하세요."}
    if "no" in anon.lower():
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": "anonymous_enable=NO로 설정하여 익명 FTP 접근을 차단하세요."}

def _u37(v):
    crontab  = _get(v, "CRONTAB")
    cron_deny = _get(v, "CRON_DENY")
    results = []
    for info in [crontab, cron_deny]:
        if not info or "NOT_FOUND" in info:
            continue
        parts = info.split()
        if len(parts) >= 2 and parts[1] == "root" and _perm_lsval_ok(parts[0], 640):
            results.append("Y")
        else:
            results.append("N")
    if not results:
        return {"result": "N/A", "improvement": "cron 파일이 존재하지 않습니다."}
    if all(r == "Y" for r in results):
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": "cron 파일 소유자를 root로, 권한을 640 이하로 설정하세요."}

def _u39(v):
    if _not_running(_get(v,"PROCESS")) and "inactive" in _get(v,"STATUS"):
        return {"result": "Y", "improvement": ""}
    if not _not_running(_get(v,"PROCESS")):
        return {"result": "PENDING", "improvement": "NFS 서비스가 실행 중입니다. 불필요하면 비활성화하고, 필요하면 접근 통제(U-40)를 확인하세요."}
    return {"result": "Y", "improvement": ""}

def _u40(v):
    proc = _get(v, "PROCESS")
    if _not_running(proc):
        return {"result": "N/A", "improvement": "NFS 서비스가 비활성화되어 있습니다."}
    exports = v.split("EXPORTS=")[1].strip() if "EXPORTS=" in v else "EMPTY"
    if exports == "EMPTY":
        return {"result": "Y", "improvement": ""}
    if "*)" in exports:
        return {"result": "N", "improvement": "/etc/exports에서 Everyone(*) 공유를 제한하세요."}
    return {"result": "PENDING", "improvement": "/etc/exports 설정을 수동으로 확인하세요."}

def _u45(v):
    if _not_running(_get(v,"SENDMAIL")) and _not_running(_get(v,"POSTFIX")):
        return {"result": "Y", "improvement": ""}
    return {"result": "PENDING", "improvement": "메일 서비스 버전을 확인하고 최신 보안 패치를 적용하세요."}

def _u46(v):
    proc = _get(v, "SENDMAIL")
    if _not_running(proc):
        return {"result": "N/A", "improvement": "Sendmail 서비스가 비활성화되어 있습니다."}
    restrict = _get(v, "RESTRICT")
    if restrict and "NOT_FOUND" not in restrict:
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": "/etc/mail/sendmail.cf에 RestrictQueueRun 옵션을 설정하세요."}

def _u47(v):
    proc = _get(v, "SENDMAIL")
    postfix = v.split("POSTFIX=")[1].strip() if "POSTFIX=" in v else "NOT_FOUND"
    if _not_running(proc) and ("NOT_FOUND" in postfix or not postfix):
        return {"result": "N/A", "improvement": "메일 서비스가 비활성화되어 있습니다."}
    if "NOT_FOUND" not in postfix and ("reject" in postfix.lower() or "mynetworks" in postfix.lower()):
        return {"result": "Y", "improvement": ""}
    return {"result": "PENDING", "improvement": "릴레이 제한 설정을 확인하세요. smtpd_recipient_restrictions에 reject 설정이 필요합니다."}

def _u48(v):
    proc = _get(v, "SENDMAIL")
    if _not_running(proc):
        return {"result": "N/A", "improvement": "Sendmail 서비스가 비활성화되어 있습니다."}
    opt = v.split("PRIVACY_OPT=")[1].strip() if "PRIVACY_OPT=" in v else "NOT_FOUND"
    if "NOT_FOUND" in opt:
        return {"result": "N", "improvement": "/etc/mail/sendmail.cf에 PrivacyOptions=noexpn,novrfy를 설정하세요."}
    if "noexpn" in opt.lower() and "novrfy" in opt.lower():
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": "PrivacyOptions에 noexpn과 novrfy를 모두 설정하세요."}

def _u49(v):
    if _not_running(_get(v,"PROCESS")):
        return {"result": "Y", "improvement": ""}
    return {"result": "PENDING", "improvement": "DNS(named) 서비스 버전을 확인하고 최신 보안 패치를 적용하세요."}

def _u50(v):
    if _not_running(_get(v,"PROCESS")):
        return {"result": "N/A", "improvement": "DNS 서비스가 비활성화되어 있습니다."}
    conf = v.split("ALLOW_TRANSFER=")[1].strip() if "ALLOW_TRANSFER=" in v else "NOT_FOUND"
    if "NOT_FOUND" in conf:
        return {"result": "N", "improvement": "/etc/named.conf에 allow-transfer { none; };를 설정하세요."}
    if "any" in conf.lower():
        return {"result": "N", "improvement": "allow-transfer { any; }를 특정 보조 DNS IP로 변경하세요."}
    if "none" in conf.lower():
        return {"result": "Y", "improvement": ""}
    return {"result": "PENDING", "improvement": "Zone Transfer 허용 대상이 적절한지 확인하세요."}

def _u51(v):
    if _not_running(_get(v,"PROCESS")):
        return {"result": "N/A", "improvement": "DNS 서비스가 비활성화되어 있습니다."}
    conf = v.split("ALLOW_UPDATE=")[1].strip() if "ALLOW_UPDATE=" in v else "NOT_FOUND"
    if "NOT_FOUND" in conf:
        return {"result": "N", "improvement": "/etc/named.conf에 allow-update { none; };를 설정하세요."}
    if "none" in conf.lower():
        return {"result": "Y", "improvement": ""}
    if "any" in conf.lower():
        return {"result": "N", "improvement": "allow-update { any; }는 위험합니다. none 또는 특정 IP로 제한하세요."}
    return {"result": "PENDING", "improvement": "DNS 동적 업데이트 설정을 수동으로 확인하세요."}

def _u52(v):
    proc   = _get(v, "PROCESS")
    status = _get(v, "STATUS")
    port   = _get(v, "PORT23")
    if _not_running(proc) and status == "inactive" and (not port or "NOT_LISTENING" in port):
        return {"result": "Y", "improvement": ""}
    if not _not_running(proc) or (port and "NOT_LISTENING" not in port):
        return {"result": "N", "improvement": "Telnet 서비스를 비활성화하고 SSH를 사용하세요. systemctl disable telnet"}
    return {"result": "Y", "improvement": ""}

def _u53(v):
    if _not_running(_get(v,"FTP_PROC")):
        return {"result": "N/A", "improvement": "FTP 서비스가 비활성화되어 있습니다."}
    banner = _get(v, "VSFTPD_BANNER")
    ident  = _get(v, "PROFTPD_IDENT")
    if banner and "NOT_SET" not in banner:
        return {"result": "Y", "improvement": ""}
    if ident and "off" in ident.lower():
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": "FTP 접속 배너에서 버전/서비스 정보를 숨기세요. vsftpd: ftpd_banner, proftpd: ServerIdent off."}

def _u54(v):
    proc   = _get(v, "FTP_PROC")
    status = _get(v, "STATUS")
    ssl    = v.split("SSL_SETTING=")[1].strip() if "SSL_SETTING=" in v else "NOT_FOUND"
    if _not_running(proc) and status == "inactive":
        return {"result": "Y", "improvement": ""}
    if not _not_running(proc):
        if "yes" in ssl.lower() or "on" in ssl.lower():
            return {"result": "Y", "improvement": ""}
        return {"result": "N", "improvement": "암호화되지 않은 FTP 서비스를 비활성화하고 SFTP 또는 FTPS로 대체하세요."}
    return {"result": "Y", "improvement": ""}

def _u55(v):
    if _not_running(_get(v,"FTP_PROC")):
        return {"result": "N/A", "improvement": "FTP 서비스가 비활성화되어 있습니다."}
    shell = _get(v, "FTP_SHELL")
    if "NOT_FOUND" in shell or "nologin" in shell or "false" in shell:
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": "ftp 계정에 /sbin/nologin 쉘을 부여하세요."}

def _u56(v):
    if _not_running(_get(v,"FTP_PROC")):
        return {"result": "N/A", "improvement": "FTP 서비스가 비활성화되어 있습니다."}
    userlist = v.split("USERLIST=")[1].split("FTPUSERS=")[0].strip() if "USERLIST=" in v else "NOT_FOUND"
    ftpusers = v.split("FTPUSERS=")[1].strip() if "FTPUSERS=" in v else "NOT_FOUND"
    if "NOT_FOUND" not in ftpusers and ftpusers.strip():
        return {"result": "Y", "improvement": ""}
    if "NOT_FOUND" not in userlist and userlist.strip():
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": "/etc/ftpusers 또는 vsftpd userlist_enable 설정으로 FTP 접근 제어를 구성하세요."}

def _u57(v):
    if _not_running(_get(v,"FTP_PROC")):
        return {"result": "N/A", "improvement": "FTP 서비스가 비활성화되어 있습니다."}
    root_in = v.split("ROOT_IN_FTPUSERS=")[1].strip() if "ROOT_IN_FTPUSERS=" in v else "NOT_FOUND"
    if "root" in root_in:
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": "/etc/ftpusers 파일에 root를 추가하여 root의 FTP 접속을 차단하세요."}

def _u58(v):
    if _not_running(_get(v,"PROCESS")) and "inactive" in _get(v,"STATUS"):
        return {"result": "Y", "improvement": ""}
    if not _not_running(_get(v,"PROCESS")):
        return {"result": "PENDING", "improvement": "SNMP 서비스가 실행 중입니다. U-59~U-61 설정을 확인하세요."}
    return {"result": "Y", "improvement": ""}

def _u59(v):
    if _not_running(_get(v,"PROCESS")):
        return {"result": "N/A", "improvement": "SNMP 서비스가 비활성화되어 있습니다."}
    v3  = v.split("V3_CONFIG=")[1].split("V1V2_CONFIG=")[0].strip() if "V3_CONFIG=" in v else "NOT_FOUND"
    v12 = v.split("V1V2_CONFIG=")[1].strip() if "V1V2_CONFIG=" in v else "NOT_FOUND"
    if "NOT_FOUND" not in v3 and v3.strip():
        return {"result": "Y", "improvement": ""}
    if "NOT_FOUND" not in v12 and v12.strip():
        return {"result": "N", "improvement": "SNMP v1/v2를 사용 중입니다. v3으로 업그레이드하세요."}
    return {"result": "PENDING", "improvement": "SNMP 버전 설정을 수동으로 확인하세요."}

def _u60(v):
    if _not_running(_get(v,"PROCESS")):
        return {"result": "N/A", "improvement": "SNMP 서비스가 비활성화되어 있습니다."}
    weak = v.split("WEAK_STRING=")[1].strip() if "WEAK_STRING=" in v else "NONE"
    if weak == "NONE" or "NONE" in weak:
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": "SNMP Community String에서 public/private를 복잡한 값으로 변경하세요."}

def _u61(v):
    if _not_running(_get(v,"PROCESS")):
        return {"result": "N/A", "improvement": "SNMP 서비스가 비활성화되어 있습니다."}
    acl = v.split("ACL_CONFIG=")[1].strip() if "ACL_CONFIG=" in v else "NOT_FOUND"
    if "NOT_FOUND" in acl or not acl.strip():
        return {"result": "N", "improvement": "/etc/snmp/snmpd.conf에 com2sec 또는 rocommunity에 접근 허용 네트워크를 설정하세요."}
    if "0.0.0.0" in acl or "default" in acl.lower():
        return {"result": "N", "improvement": "SNMP 접근이 모든 IP에 허용되어 있습니다. 관리 네트워크 대역으로 제한하세요."}
    return {"result": "Y", "improvement": ""}

def _u62(v):
    motd   = v.split("MOTD=")[1].split("ISSUE=")[0].strip() if "MOTD=" in v else "EMPTY"
    banner = v.split("SSH_BANNER=")[1].strip() if "SSH_BANNER=" in v else "NOT_SET"
    if motd not in ("EMPTY","NOT_FOUND","") and len(motd) > 5:
        return {"result": "Y", "improvement": ""}
    if "NOT_SET" not in banner and "none" not in banner.lower():
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": "/etc/motd에 경고 메시지를 작성하거나 /etc/ssh/sshd_config에 Banner를 설정하세요."}

def _u63(v):
    perm = _get(v, "SUDOERS_PERM")
    if "NOT_FOUND" in perm:
        return {"result": "N/A", "improvement": "/etc/sudoers 파일이 없습니다."}
    parts = perm.split()
    if len(parts) >= 2 and parts[1] == "root" and _perm_lsval_ok(parts[0], 640):
        nopasswd = v.split("NOPASSWD=")[1].strip() if "NOPASSWD=" in v else "NONE"
        if nopasswd and nopasswd != "NONE":
            return {"result": "PENDING", "improvement": f"NOPASSWD 설정이 존재합니다: {nopasswd}. 불필요한 설정을 제거하세요."}
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": "/etc/sudoers 소유자를 root로, 권한을 640으로 설정하세요."}

def _u64_pending(v):
    kernel = _get(v, "KERNEL")
    return {"result": "PENDING", "improvement": f"OS 및 커널({kernel}) 버전을 확인하고 최신 보안 패치 적용 여부를 인터뷰로 확인하세요."}

def _u65(v):
    ntp_ok    = "active" in _get(v, "NTP_STATUS")
    chrony_ok = "active" in _get(v, "CHRONY_STATUS")
    sync      = v.split("SYNC=")[1].strip() if "SYNC=" in v else "NOT_SYNCED"
    ntp_conf    = _get(v, "NTP_CONF")
    chrony_conf = _get(v, "CHRONY_CONF")
    has_server = (ntp_conf and "NOT_FOUND" not in ntp_conf) or (chrony_conf and "NOT_FOUND" not in chrony_conf)
    if (ntp_ok or chrony_ok) and has_server and "NOT_SYNCED" not in sync:
        return {"result": "Y", "improvement": ""}
    if not ntp_ok and not chrony_ok:
        return {"result": "N", "improvement": "NTP 서비스(ntpd 또는 chronyd)를 활성화하고 NTP 서버를 설정하세요."}
    if not has_server:
        return {"result": "N", "improvement": "/etc/ntp.conf 또는 /etc/chrony.conf에 NTP 서버를 설정하세요."}
    return {"result": "PENDING", "improvement": "NTP 동기화 상태를 ntpq -pn 또는 chronyc tracking으로 확인하세요."}

def _u66(v):
    status = _get(v, "STATUS")
    conf   = v.split("CONF=")[1].strip() if "CONF=" in v else "NOT_FOUND"
    if "inactive" in status:
        return {"result": "N", "improvement": "rsyslog 서비스를 활성화하고 로깅 정책을 설정하세요."}
    if "active" in status and "NOT_FOUND" not in conf:
        required = ["messages", "secure", "cron"]
        if all(r in conf for r in required):
            return {"result": "Y", "improvement": ""}
        missing = [r for r in required if r not in conf]
        return {"result": "PENDING", "improvement": f"rsyslog에 필수 로그 항목이 누락되어 있습니다: {missing}."}
    return {"result": "PENDING", "improvement": "시스템 로깅 설정을 수동으로 확인하세요."}

def _u67(v):
    varlog   = _get(v, "VARLOG_PERM")
    bad      = v.split("BAD_PERM_FILES=")[1].split("NON_ROOT_OWNED=")[0].strip() if "BAD_PERM_FILES=" in v else "NONE"
    non_root = v.split("NON_ROOT_OWNED=")[1].strip() if "NON_ROOT_OWNED=" in v else "NONE"
    if "NOT_FOUND" in varlog:
        return {"result": "N", "improvement": "/var/log 디렉터리가 존재하지 않습니다."}
    if (not bad or bad == "NONE") and (not non_root or non_root == "NONE"):
        return {"result": "Y", "improvement": ""}
    tips = []
    if bad and bad != "NONE":
        tips.append(f"권한이 644 초과인 로그 파일: {bad}.")
    if non_root and non_root != "NONE":
        tips.append(f"root 이외 소유자의 로그 파일: {non_root}.")
    tips.append("chown root /var/log/<파일> && chmod 644 /var/log/<파일>로 설정하세요.")
    return {"result": "N", "improvement": " ".join(tips)}
