#!/bin/bash
# linux_scan.sh
# 점검 대상 서버에서 실행하는 스크립트
# 실행 방법: bash linux_scan.sh > result.txt

echo "===CCE_SCAN_START==="
echo "SCAN_DATE|$(date '+%Y-%m-%d %H:%M:%S')"
echo "HOSTNAME|$(hostname)"
echo "OS|$(cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2 | tr -d '"')"

# ── 계정 관리 ──────────────────────────────────────────
# U-01: root 계정 원격 접속 제한
echo "U-01|$(grep '^PermitRootLogin' /etc/ssh/sshd_config 2>/dev/null | awk '{print $2}' || echo 'NOT_FOUND')"

# U-02: 비밀번호 복잡성 설정
echo "U-02|$(grep -E '^minlen|^dcredit|^ucredit|^lcredit|^ocredit' /etc/security/pwquality.conf 2>/dev/null | tr '\n' ' ' || echo 'NOT_FOUND')"

# U-03: 계정 잠금 임계값 설정
echo "U-03|$(grep -E '^deny' /etc/security/faillock.conf 2>/dev/null || grep 'deny=' /etc/pam.d/system-auth 2>/dev/null | head -1 || echo 'NOT_FOUND')"

# U-04: 비밀번호 파일 보호
echo "U-04|$(passwd -S root 2>/dev/null | awk '{print $2}' || echo 'NOT_FOUND')"

# U-05: root 이외의 UID=0 계정 확인
echo "U-05|$(awk -F: '($3==0 && $1!="root"){print $1}' /etc/passwd 2>/dev/null || echo 'NONE')"

# U-11: 홈 디렉터리 권한 설정
echo "U-11|$(ls -ld /home/*/ 2>/dev/null | awk '{print $1, $3, $9}' | tr '\n' ';' || echo 'NOT_FOUND')"

# ── 파일 및 디렉터리 관리 ───────────────────────────────
# U-14: /etc/passwd 파일 소유자 및 권한
echo "U-14|$(stat -c '%U %a' /etc/passwd 2>/dev/null || echo 'NOT_FOUND')"

# U-15: /etc/shadow 파일 소유자 및 권한
echo "U-15|$(stat -c '%U %a' /etc/shadow 2>/dev/null || echo 'NOT_FOUND')"

# U-16: /etc/hosts 파일 소유자 및 권한
echo "U-16|$(stat -c '%U %a' /etc/hosts 2>/dev/null || echo 'NOT_FOUND')"

# U-17: /etc/inetd.conf 파일 소유자 및 권한
echo "U-17|$(stat -c '%U %a' /etc/inetd.conf 2>/dev/null || stat -c '%U %a' /etc/xinetd.conf 2>/dev/null || echo 'NOT_FOUND')"

# U-18: /etc/syslog.conf 파일 소유자 및 권한
echo "U-18|$(stat -c '%U %a' /etc/syslog.conf 2>/dev/null || stat -c '%U %a' /etc/rsyslog.conf 2>/dev/null || echo 'NOT_FOUND')"

# U-19: /etc/services 파일 소유자 및 권한
echo "U-19|$(stat -c '%U %a' /etc/services 2>/dev/null || echo 'NOT_FOUND')"

# U-20: SUID/SGID 파일 점검
echo "U-20|$(find / -type f \( -perm -4000 -o -perm -2000 \) 2>/dev/null | head -20 | tr '\n' ';' || echo 'NOT_FOUND')"

# U-21: 시작파일 및 환경파일 소유자 및 권한
echo "U-21|$(stat -c '%U %a' /etc/profile 2>/dev/null || echo 'NOT_FOUND')"

# U-22: 세계 쓰기 가능 파일 점검
echo "U-22|$(find / -type f -perm -002 -not -path '/proc/*' 2>/dev/null | head -10 | tr '\n' ';' || echo 'NONE')"

# U-23: /dev에 존재하지 않는 device 파일 점검
echo "U-23|$(find /dev -type f -not -name '.*' 2>/dev/null | head -5 | tr '\n' ';' || echo 'NONE')"

# U-24: .rhosts, hosts.equiv 사용 금지
echo "U-24|$(find /home -name '.rhosts' 2>/dev/null; find /etc -name 'hosts.equiv' 2>/dev/null | tr '\n' ';' || echo 'NONE')"

# U-25: 접속 IP 및 포트 제한
echo "U-25|$(cat /etc/hosts.allow 2>/dev/null | grep -v '^#' | head -5 | tr '\n' ';' || echo 'NOT_FOUND')"

# U-26: hosts.lpd 파일 권한
echo "U-26|$(stat -c '%U %a' /etc/hosts.lpd 2>/dev/null || echo 'NOT_FOUND')"

# U-27: NIS 서비스 비활성화
echo "U-27|$(systemctl is-active ypbind 2>/dev/null || echo 'inactive')"

# U-29: 홈 디렉터리 공유파일 관리
echo "U-29|$(find /home -name '.netrc' -o -name '.rhosts' 2>/dev/null | tr '\n' ';' || echo 'NONE')"

# U-30: 숨겨진 파일 및 디렉터리 점검
echo "U-30|$(find / -name '.*' -maxdepth 3 -not -path '/proc/*' 2>/dev/null | head -10 | tr '\n' ';' || echo 'NONE')"

# U-31: Cron 파일 소유자 및 권한
echo "U-31|$(stat -c '%U %a' /etc/crontab 2>/dev/null || echo 'NOT_FOUND')"

# U-32: at 파일 소유자 및 권한
echo "U-32|$(stat -c '%U %a' /etc/at.allow 2>/dev/null || stat -c '%U %a' /etc/at.deny 2>/dev/null || echo 'NOT_FOUND')"

# U-33: rsyslog.conf 파일 권한
echo "U-33|$(stat -c '%U %a' /etc/rsyslog.conf 2>/dev/null || echo 'NOT_FOUND')"

# ── 서비스 관리 ────────────────────────────────────────
# U-34: finger 서비스 비활성화
echo "U-34|$(systemctl is-active finger 2>/dev/null || echo 'inactive')"

# U-35: Anonymous FTP 비활성화
echo "U-35|$(grep -i 'anonymous_enable' /etc/vsftpd.conf 2>/dev/null || echo 'NOT_FOUND')"

# U-36: r 계열 서비스 비활성화
echo "U-36|$(systemctl is-active rsh 2>/dev/null; systemctl is-active rlogin 2>/dev/null; systemctl is-active rexec 2>/dev/null | tr '\n' ';')"

# U-38: DoS 공격 취약 서비스 비활성화
echo "U-38|$(systemctl is-active chargen 2>/dev/null; systemctl is-active daytime 2>/dev/null; systemctl is-active echo 2>/dev/null | tr '\n' ';')"

# U-39: NFS 서비스 비활성화
echo "U-39|$(systemctl is-active nfs-server 2>/dev/null || systemctl is-active nfs 2>/dev/null || echo 'inactive')"

# U-40: NFS 접근 통제
echo "U-40|$(cat /etc/exports 2>/dev/null | grep -v '^#' || echo 'NOT_FOUND')"

# U-41: automountd 제거
echo "U-41|$(systemctl is-active autofs 2>/dev/null || echo 'inactive')"

# U-42: RPC 서비스 확인
echo "U-42|$(systemctl is-active rpcbind 2>/dev/null || echo 'inactive')"

# U-44: tftp, talk 서비스 비활성화
echo "U-44|$(systemctl is-active tftp 2>/dev/null; systemctl is-active talk 2>/dev/null | tr '\n' ';')"

# U-45: Sendmail 버전 점검
echo "U-45|$(sendmail -d0.1 -bv root 2>/dev/null | grep -i version | head -1 || echo 'NOT_FOUND')"

# U-46: 스팸 메일 릴레이 제한
echo "U-46|$(grep -i 'smtpd_recipient_restrictions' /etc/postfix/main.cf 2>/dev/null || echo 'NOT_FOUND')"

# U-47: 일반 사용자 Sendmail 실행 방지
echo "U-47|$(grep 'RestrictQueueRun' /etc/mail/sendmail.cf 2>/dev/null || echo 'NOT_FOUND')"

# U-49: DNS Zone Transfer 설정
echo "U-49|$(grep -i 'allow-transfer' /etc/named.conf 2>/dev/null || echo 'NOT_FOUND')"

# U-50: Apache 웹 서비스 정보 숨김
echo "U-50|$(grep -i 'ServerTokens' /etc/httpd/conf/httpd.conf 2>/dev/null || grep -i 'ServerTokens' /etc/apache2/apache2.conf 2>/dev/null || echo 'NOT_FOUND')"

# U-51: DNS 동적 업데이트 설정
echo "U-51|$(grep -i 'allow-update' /etc/named.conf 2>/dev/null || echo 'NOT_FOUND')"

# U-52: FTP 서비스 확인
echo "U-52|$(systemctl is-active vsftpd 2>/dev/null || systemctl is-active ftp 2>/dev/null || echo 'inactive')"

# U-53: FTP 계정 shell 제한
echo "U-53|$(grep 'ftpusers' /etc/shells 2>/dev/null || cat /etc/ftpusers 2>/dev/null | head -5 || echo 'NOT_FOUND')"

# U-54: Ftpusers 파일 소유자 및 권한
echo "U-54|$(stat -c '%U %a' /etc/ftpusers 2>/dev/null || echo 'NOT_FOUND')"

# U-55: Ftpusers 파일 설정
echo "U-55|$(cat /etc/ftpusers 2>/dev/null | grep root || echo 'NOT_FOUND')"

# U-56: at 서비스 권한 설정
echo "U-56|$(stat -c '%U %a' /etc/at.allow 2>/dev/null || echo 'NOT_FOUND')"

# U-57: SNMP 서비스 구동 점검
echo "U-57|$(systemctl is-active snmpd 2>/dev/null || echo 'inactive')"

# U-58: SNMP Community String 복잡성
echo "U-58|$(grep '^community\|^rocommunity\|^rwcommunity' /etc/snmp/snmpd.conf 2>/dev/null || echo 'NOT_FOUND')"

# U-60: 보안 패치 적용 확인
echo "U-60|$(uname -r 2>/dev/null || echo 'NOT_FOUND')"

# U-61: SSH 보안 버전 사용
echo "U-61|$(ssh -V 2>&1 || echo 'NOT_FOUND')"

# U-62: FTP Bounce Attack 점검
echo "U-62|$(grep -i 'port_promiscuous\|deny_file' /etc/vsftpd.conf 2>/dev/null || echo 'NOT_FOUND')"

# U-63: 웹 서비스 디렉토리 리스팅 제거
echo "U-63|$(grep -i 'Options.*Indexes' /etc/httpd/conf/httpd.conf 2>/dev/null || grep -i 'autoindex' /etc/nginx/nginx.conf 2>/dev/null || echo 'NOT_FOUND')"

# ── 로그 관리 ─────────────────────────────────────────
# U-65: 로그온 기록 검토 설정
echo "U-65|$(last 2>/dev/null | head -5 | tr '\n' ';' || echo 'NOT_FOUND')"

# U-66: 시스템 로깅 설정
echo "U-66|$(systemctl is-active rsyslog 2>/dev/null || systemctl is-active syslog 2>/dev/null || echo 'inactive')"

# U-67: NTP 서비스 설정
echo "U-67|$(systemctl is-active ntpd 2>/dev/null || systemctl is-active chronyd 2>/dev/null || echo 'inactive')"

echo "===CCE_SCAN_END==="
