# parsers/linux.py
# 판단 로직이 있는 항목 → 자동 판단 (Y/N/N/A)
# 판단 로직이 없는 항목 → PENDING (UI에서 점검자가 직접 입력)

def parse_result_file(content: str) -> dict:
    """스크립트 결과 텍스트를 파싱해서 딕셔너리로 반환"""
    results = {}
    lines = content.strip().split("\n")

    for line in lines:
        line = line.strip()
        if "|" not in line:
            continue
        if line.startswith(("SCAN_DATE", "HOSTNAME", "OS", "===")):
            continue
        code, _, value = line.partition("|")
        results[code.strip()] = value.strip()

    return results


def judge_result(code: str, value: str) -> dict:
    """
    판단 로직이 있으면 자동 판단, 없으면 PENDING 반환
    반환: {"result": "Y"/"N"/"N/A"/"PENDING", "improvement": "..."}
    """
    # 점검 불가 항목
    if value == "NOT_FOUND":
        return {"result": "N/A", "improvement": "해당 설정 파일을 찾을 수 없습니다."}

    # 판단 로직이 있는 항목 목록
    judges = {
        "U-01": _judge_u01,
        "U-02": _judge_u02,
        "U-03": _judge_u03,
        "U-04": _judge_u04,
        "U-05": _judge_u05,
        "U-14": _judge_file_owner_root,
        "U-15": _judge_shadow,
        "U-16": _judge_file_owner_root,
        "U-18": _judge_file_owner_root,
        "U-19": _judge_file_owner_root,
        "U-27": _judge_service_inactive,
        "U-34": _judge_service_inactive,
        "U-39": _judge_service_inactive,
        "U-41": _judge_service_inactive,
        "U-42": _judge_rpc,
        "U-44": _judge_service_inactive,
        "U-52": _judge_ftp,
        "U-57": _judge_snmp,
        "U-66": _judge_service_active,
        "U-67": _judge_ntp,
    }

    judge_func = judges.get(code)
    if judge_func:
        return judge_func(value)

    # 판단 로직 없는 항목 → PENDING (점검자가 UI에서 직접 입력)
    return {
        "result": "PENDING",
        "improvement": ""
    }


# ── 판단 함수 ────────────────────────────────────────

def _judge_u01(value: str) -> dict:
    """U-01: root 원격 접속 제한"""
    if value.lower() in ["no", "prohibit-password"]:
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": "/etc/ssh/sshd_config에서 PermitRootLogin no로 설정하세요."}

def _judge_u02(value: str) -> dict:
    """U-02: 패스워드 복잡성 — minlen=8 이상이면 양호"""
    if "minlen" in value:
        try:
            minlen = int(value.split("minlen=")[1].split()[0])
            if minlen >= 8:
                return {"result": "Y", "improvement": ""}
        except Exception:
            pass
    return {"result": "N", "improvement": "/etc/security/pwquality.conf에서 minlen=8 이상으로 설정하세요."}

def _judge_u03(value: str) -> dict:
    """U-03: 계정 잠금 임계값 — deny=5 이하이면 양호"""
    if "deny" in value:
        try:
            deny = int(value.split("deny=")[1].split()[0].rstrip(';'))
            if 1 <= deny <= 5:
                return {"result": "Y", "improvement": ""}
        except Exception:
            pass
    return {"result": "N", "improvement": "계정 잠금 임계값을 5 이하로 설정하세요."}

def _judge_u04(value: str) -> dict:
    """U-04: 패스워드 파일 보호 — P이면 양호"""
    if value == "P":
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": "root 계정에 패스워드를 설정하세요."}

def _judge_u05(value: str) -> dict:
    """U-05: UID=0 계정 — NONE이면 양호"""
    if value in ["NONE", ""]:
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": f"UID가 0인 불필요한 계정({value})을 삭제하거나 UID를 변경하세요."}

def _judge_file_owner_root(value: str) -> dict:
    """파일 소유자가 root이고 권한이 644 이하이면 양호"""
    try:
        owner, perm = value.split()
        if owner == "root" and int(perm) <= 644:
            return {"result": "Y", "improvement": ""}
    except Exception:
        pass
    return {"result": "N", "improvement": "파일 소유자를 root로, 권한을 644 이하로 설정하세요."}

def _judge_shadow(value: str) -> dict:
    """U-15: shadow 파일 권한 — root 소유 400 이하이면 양호"""
    try:
        owner, perm = value.split()
        if owner == "root" and int(perm) <= 400:
            return {"result": "Y", "improvement": ""}
    except Exception:
        pass
    return {"result": "N", "improvement": "/etc/shadow 파일 소유자를 root로, 권한을 400 이하로 설정하세요."}

def _judge_service_inactive(value: str) -> dict:
    """서비스가 inactive이면 양호"""
    if "inactive" in value or "not-found" in value:
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": "해당 서비스를 비활성화하세요."}

def _judge_service_active(value: str) -> dict:
    """서비스가 active이면 양호 (로깅 등)"""
    if "active" in value:
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": "해당 서비스를 활성화하세요."}

def _judge_rpc(value: str) -> dict:
    """U-42: RPC 서비스 — 불필요하면 비활성화"""
    if "inactive" in value or "not-found" in value:
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": "불필요한 경우 RPC 서비스를 비활성화하세요."}

def _judge_ftp(value: str) -> dict:
    """U-52: FTP 서비스 — inactive이면 양호"""
    if "inactive" in value or "not-found" in value:
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": "FTP 서비스 사용 여부를 검토하고 불필요하면 비활성화하세요."}

def _judge_snmp(value: str) -> dict:
    """U-57: SNMP 서비스 — inactive이면 양호"""
    if "inactive" in value or "not-found" in value:
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": "SNMP 서비스 사용 여부를 검토하고 불필요하면 비활성화하세요."}

def _judge_ntp(value: str) -> dict:
    """U-67: NTP 서비스 — active이면 양호"""
    if "active" in value:
        return {"result": "Y", "improvement": ""}
    return {"result": "N", "improvement": "NTP 서비스(ntpd 또는 chronyd)를 활성화하세요."}
