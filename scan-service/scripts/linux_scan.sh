#!/bin/bash
# linux_scan.sh
# 주요정보통신기반시설 기술적 취약점 분석·평가 방법 상세가이드 (2026) 기준
# Unix 서버 U-01 ~ U-67 전체 항목 점검
# 실행 방법: bash linux_scan.sh > result.txt

echo "===CCE_SCAN_START==="
echo "SCAN_DATE|$(date '+%Y-%m-%d %H:%M:%S')"
echo "HOSTNAME|$(hostname)"
echo "OS|$(grep PRETTY_NAME /etc/os-release 2>/dev/null | cut -d= -f2 | tr -d '"')"
echo "KERNEL|$(uname -r 2>/dev/null)"
echo "IP|$(ip addr 2>/dev/null | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | tr '\n' ' ')"

# ── 1. 계정 관리 ──────────────────────────────────────────────────────────────

# U-01: root 계정 원격 접속 제한
U01_SSHD=$(grep -i '^PermitRootLogin' /etc/ssh/sshd_config 2>/dev/null | awk '{print $2}')
U01_SECURETTY=$(grep -i '^pts' /etc/securetty 2>/dev/null | tr '\n' ' ')
U01_PAM=$(grep -i 'pam_securetty.so' /etc/pam.d/sshd 2>/dev/null | grep -v '^#' | head -1)
echo "U-01|SSHD=${U01_SSHD:-NOT_FOUND} SECURETTY_PTS=${U01_SECURETTY:-NONE} PAM_SECURETTY=${U01_PAM:-NOT_SET}"

# U-02: 비밀번호 관리정책 설정 (복잡성)
U02_PAM=$(grep 'pam_pwquality.so\|pam_cracklib.so' /etc/pam.d/system-auth 2>/dev/null | grep -v '^#' | head -1)
U02_CONF=$(grep -v '^ *#' /etc/security/pwquality.conf 2>/dev/null | grep -E 'minlen|dcredit|ucredit|lcredit|ocredit|minclass' | tr '\n' ' ')
echo "U-02|PAM=${U02_PAM:-NOT_SET} CONF=${U02_CONF:-NOT_FOUND}"

# U-03: 계정 잠금 임계값 설정
U03_SYS=$(grep 'pam_faillock.so\|pam_tally' /etc/pam.d/system-auth 2>/dev/null | grep 'deny=' | head -1)
U03_PWD=$(grep 'pam_faillock.so\|pam_tally' /etc/pam.d/password-auth 2>/dev/null | grep 'deny=' | head -1)
U03_CONF=$(grep -E '^deny' /etc/security/faillock.conf 2>/dev/null | head -1)
echo "U-03|SYSTEM_AUTH=${U03_SYS:-NOT_SET} PASSWORD_AUTH=${U03_PWD:-NOT_SET} FAILLOCK_CONF=${U03_CONF:-NOT_FOUND}"

# U-04: 비밀번호 파일 보호 (shadow 사용 여부)
U04_SHADOW=$(ls -l /etc/shadow 2>/dev/null | awk '{print $1, $3, $4}')
U04_ENCRYPT=$(grep -i 'ENCRYPT_METHOD' /etc/login.defs 2>/dev/null | grep -v '^#')
U04_PASSWD_CHECK=$(awk -F: 'NR<=3{print $2}' /etc/passwd 2>/dev/null | grep -v '^x$' | head -1)
echo "U-04|SHADOW_PERM=${U04_SHADOW:-NOT_FOUND} ENCRYPT=${U04_ENCRYPT:-NOT_FOUND} PASSWD_FIELD=${U04_PASSWD_CHECK:-x}"

# U-05: root 이외의 UID가 '0' 금지
U05=$(awk -F: '($3==0 && $1!="root"){print $1}' /etc/passwd 2>/dev/null)
echo "U-05|${U05:-NONE}"

# U-06: 사용자 계정 su 기능 제한
U06_PERM=$(ls -l /bin/su 2>/dev/null | awk '{print $1, $3, $4}')
U06_SU_GRP=$(stat -c '%G' /bin/su 2>/dev/null)
U06_GRP_MEMBERS=$(grep "^${U06_SU_GRP}:" /etc/group 2>/dev/null | cut -d: -f4)
U06_PAM=$(grep 'pam_wheel.so' /etc/pam.d/su 2>/dev/null | grep -v '^#' | head -1)
echo "U-06|SU_PERM=${U06_PERM:-NOT_FOUND} SU_GROUP=${U06_SU_GRP:-NONE} GROUP_MEMBERS=${U06_GRP_MEMBERS:-NONE} PAM=${U06_PAM:-NOT_SET}"

# U-07: 불필요한 계정 제거
U07=$(awk -F: '{if($3==0 || ($3>=1000 && $3<=60000)) print "["$1"]["$7"]"}' /etc/passwd 2>/dev/null | tr '\n' ' ')
echo "U-07|${U07:-NOT_FOUND}"

# U-08: 관리자 그룹에 최소한의 계정 포함
U08=$(grep ':0:' /etc/group 2>/dev/null | awk -F: '{print "["$1"]["$4"]"}' | tr '\n' ' ')
echo "U-08|${U08:-NONE}"

# U-09: 계정이 존재하지 않는 GID 금지
U09=$(awk -F: '{print $4}' /etc/passwd 2>/dev/null | sort -u | while read gid; do
  grep -q ":${gid}:" /etc/group 2>/dev/null || echo "MISSING_GID:${gid}"
done | tr '\n' ' ')
echo "U-09|${U09:-NONE}"

# U-10: 동일한 UID 금지
U10=$(awk -F: '{print $3}' /etc/passwd 2>/dev/null | sort | uniq -d | while read uid; do
  users=$(awk -F: -v u="$uid" '$3==u{print $1}' /etc/passwd | tr '\n' ',')
  echo "DUP_UID=${uid}:${users}"
done | tr '\n' ' ')
echo "U-10|${U10:-NONE}"

# U-11: 사용자 Shell 점검
U11=$(awk -F: '{if($7!~/nologin|false|sync|shutdown|halt/ && $3!=0 && $3<1000) print "["$1"]["$3"]["$7"]"}' /etc/passwd 2>/dev/null | tr '\n' ' ')
echo "U-11|${U11:-NONE}"

# U-12: 세션 종료 시간 설정 (TMOUT)
U12_PROFILE=$(grep -i 'TMOUT' /etc/profile 2>/dev/null | grep -v '^#' | tr '\n' ' ')
U12_BASHRC=$(grep -i 'TMOUT' /etc/bashrc 2>/dev/null | grep -v '^#' | head -1)
U12_PROFILED=$(grep -ri 'TMOUT' /etc/profile.d/ 2>/dev/null | grep -v '^#' | head -2 | tr '\n' ';')
echo "U-12|PROFILE=${U12_PROFILE:-NOT_SET} BASHRC=${U12_BASHRC:-NOT_SET} PROFILE_D=${U12_PROFILED:-NOT_SET}"

# U-13: 안전한 비밀번호 암호화 알고리즘 사용 (SHA-256/512)
U13_LOGINDEFS=$(grep '^ENCRYPT_METHOD' /etc/login.defs 2>/dev/null)
U13_PAM=$(grep 'pam_unix.so' /etc/pam.d/system-auth 2>/dev/null | grep 'password' | grep -v '^#' | head -1)
U13_SHADOW_ALGO=$(awk -F: '($3>=1000 || $3==0) && $2~/^\$/ {split($2,a,"$"); print $1":"a[2]}' /etc/shadow 2>/dev/null | head -5 | tr '\n' ' ')
echo "U-13|LOGIN_DEFS=${U13_LOGINDEFS:-NOT_FOUND} PAM=${U13_PAM:-NOT_SET} SHADOW_ALGO=${U13_SHADOW_ALGO:-NOT_FOUND}"

# ── 2. 파일 및 디렉터리 관리 ──────────────────────────────────────────────────

# U-14: root 홈, 패스 디렉터리 권한 및 패스 설정
U14_PATH=$(su - root -c 'echo $PATH' 2>/dev/null || echo "$PATH")
U14_HOME=$(ls -ld /root 2>/dev/null | awk '{print $1, $3, $4}')
echo "U-14|PATH=${U14_PATH:-NOT_FOUND} ROOT_HOME=${U14_HOME:-NOT_FOUND}"

# U-15: 파일 및 디렉터리 소유자 설정
U15=$(for dir in /bin /sbin /home /lib /usr /var /etc; do
  result=$(find "$dir" -nouser -o -nogroup 2>/dev/null | head -3)
  [ -n "$result" ] && echo "${dir}:${result}"
done | tr '\n' ';')
echo "U-15|${U15:-NONE}"

# U-16: /etc/passwd 파일 소유자 및 권한 설정
echo "U-16|$(ls -l /etc/passwd 2>/dev/null | awk '{print $1, $3, $4}' || echo 'NOT_FOUND')"

# U-17: 시스템 시작 스크립트 권한 설정
U17_RCD=$(ls -al /etc/rc.d/rc*.d/ 2>/dev/null | awk '{print $1,$3,$4,$9}' | grep -v '^total\|^d\.\.' | head -10 | tr '\n' ';')
U17_INITD=$(ls -al /etc/init.d/ 2>/dev/null | awk '{print $1,$3,$4,$9}' | grep -v '^total\|^d\.\.' | head -10 | tr '\n' ';')
U17_SYSTEMD=$(ls -al /etc/systemd/system/ 2>/dev/null | awk '{print $1,$3,$4,$9}' | grep -v '^total\|^d\.\.' | head -5 | tr '\n' ';')
echo "U-17|RC_D=${U17_RCD:-NOT_FOUND} INIT_D=${U17_INITD:-NOT_FOUND} SYSTEMD=${U17_SYSTEMD:-NOT_FOUND}"

# U-18: /etc/shadow 파일 소유자 및 권한 설정
echo "U-18|$(ls -l /etc/shadow 2>/dev/null | awk '{print $1, $3, $4}' || echo 'NOT_FOUND')"

# U-19: /etc/hosts 파일 소유자 및 권한 설정
echo "U-19|$(ls -l /etc/hosts 2>/dev/null | awk '{print $1, $3, $4}' || echo 'NOT_FOUND')"

# U-20: /etc/(x)inetd.conf 파일 소유자 및 권한 설정
U20_INETD=$(ls -l /etc/inetd.conf 2>/dev/null | awk '{print $1, $3, $4}')
U20_XINETD=$(ls -l /etc/xinetd.conf 2>/dev/null | awk '{print $1, $3, $4}')
U20_XINETDD=$(ls -al /etc/xinetd.d/* 2>/dev/null | awk '{print $1,$3,$4,$9}' | tr '\n' ';')
echo "U-20|INETD=${U20_INETD:-NOT_FOUND} XINETD=${U20_XINETD:-NOT_FOUND} XINETD_D=${U20_XINETDD:-NOT_FOUND}"

# U-21: /etc/(r)syslog.conf 파일 소유자 및 권한 설정
U21_SYSLOG=$(ls -l /etc/syslog.conf 2>/dev/null | awk '{print $1, $3, $4}')
U21_RSYSLOG=$(ls -l /etc/rsyslog.conf 2>/dev/null | awk '{print $1, $3, $4}')
echo "U-21|SYSLOG=${U21_SYSLOG:-NOT_FOUND} RSYSLOG=${U21_RSYSLOG:-NOT_FOUND}"

# U-22: /etc/services 파일 소유자 및 권한 설정
echo "U-22|$(ls -l /etc/services 2>/dev/null | awk '{print $1, $3, $4}' || echo 'NOT_FOUND')"

# U-23: SUID, SGID, Sticky bit 설정 파일 점검
U23_DANGEROUS="/sbin/dump /usr/bin/lpq /usr/bin/lpr /usr/bin/lprm /usr/bin/newgrp /usr/bin/at /sbin/restore /usr/sbin/lpc /usr/sbin/traceroute /sbin/unix_chkpwd"
U23_FOUND=$(for f in $U23_DANGEROUS; do [ -f "$f" ] && ls -l "$f" 2>/dev/null | awk '{print $1,$9}'; done | tr '\n' ';')
U23_ALL=$(find / -type f \( -perm -4000 -o -perm -2000 \) 2>/dev/null | head -20 | tr '\n' ';')
echo "U-23|DANGEROUS=${U23_FOUND:-NONE} ALL_SUID=${U23_ALL:-NONE}"

# U-24: 사용자, 시스템 환경변수 파일 소유자 및 권한 설정
U24_PROFILE=$(ls -l /etc/profile 2>/dev/null | awk '{print $1, $3, $4}')
U24_BASHRC=$(ls -l /etc/bashrc 2>/dev/null | awk '{print $1, $3, $4}')
U24_USER=$(awk -F: '($3>=1000 && $3<60000) || $3==0 {print $1,$6}' /etc/passwd 2>/dev/null | while read user home; do
  for f in .bash_profile .bashrc .profile .cshrc; do
    [ -f "${home}/${f}" ] && ls -l "${home}/${f}" 2>/dev/null | awk -v u="$user" '{print u":"$1,$3,$4,$9}'
  done
done | tr '\n' ';')
echo "U-24|ETC_PROFILE=${U24_PROFILE:-NOT_FOUND} ETC_BASHRC=${U24_BASHRC:-NOT_FOUND} USER_FILES=${U24_USER:-NOT_FOUND}"

# U-25: world writable 파일 점검
U25=$(find / -type f -perm -002 -not -path '/proc/*' -not -path '/sys/*' -not -path '/dev/*' 2>/dev/null | head -10 | tr '\n' ';')
echo "U-25|${U25:-NONE}"

# U-26: /dev에 존재하지 않는 device 파일 점검
U26=$(find /dev -type f -not -name '.*' 2>/dev/null | head -10 | tr '\n' ';')
echo "U-26|${U26:-NONE}"

# U-27: $HOME/.rhosts, hosts.equiv 사용 금지
U27_EQUIV=$(ls -al /etc/hosts.equiv 2>/dev/null | awk '{print $1, $3, $4}')
U27_RHOSTS=$(find /home /root -name '.rhosts' 2>/dev/null | tr '\n' ';')
U27_RSH_SVC=$(ls /etc/xinetd.d/ 2>/dev/null | grep -E 'rsh|rlogin|rexec')
echo "U-27|HOSTS_EQUIV=${U27_EQUIV:-NOT_FOUND} RHOSTS=${U27_RHOSTS:-NONE} R_XINETD=${U27_RSH_SVC:-NOT_FOUND}"

# U-28: 접속 IP 및 포트 제한
U28_DENY=$(grep -v '^#' /etc/hosts.deny 2>/dev/null | grep -v '^$' | tr '\n' ';')
U28_ALLOW=$(grep -v '^#' /etc/hosts.allow 2>/dev/null | grep -v '^$' | tr '\n' ';')
echo "U-28|HOSTS_DENY=${U28_DENY:-EMPTY} HOSTS_ALLOW=${U28_ALLOW:-EMPTY}"

# U-29: hosts.lpd 파일 소유자 및 권한 설정
echo "U-29|$(ls -l /etc/hosts.lpd 2>/dev/null | awk '{print $1, $3, $4}' || echo 'NOT_FOUND')"

# U-30: UMASK 설정 관리
U30_CURRENT=$(umask 2>/dev/null)
U30_PROFILE=$(grep -v '^#' /etc/profile 2>/dev/null | grep 'umask' | tr '\n' ' ')
U30_BASHRC=$(grep -v '^#' /etc/bashrc 2>/dev/null | grep 'umask' | tr '\n' ' ')
echo "U-30|CURRENT=${U30_CURRENT:-NOT_FOUND} PROFILE=${U30_PROFILE:-NOT_SET} BASHRC=${U30_BASHRC:-NOT_SET}"

# U-31: 홈 디렉토리 소유자 및 권한 설정
U31=$(awk -F: '($3>=1000 && $3<60000) || $3==0 {print $1,$6}' /etc/passwd 2>/dev/null | while read user home; do
  [ -d "$home" ] && ls -ald "$home" 2>/dev/null | awk -v u="[$user]" '{print u" "$1,$3,$4,$9}'
done | tr '\n' ';')
echo "U-31|${U31:-NOT_FOUND}"

# U-32: 홈 디렉토리로 지정한 디렉토리의 존재 관리
U32=$(awk -F: '($3>=1000 && $3<60000) || $3==0 {print $1,$6,$7}' /etc/passwd 2>/dev/null | while read user home shell; do
  echo "$shell" | grep -qE 'nologin|false' && continue
  [ ! -d "$home" ] && echo "NO_HOME:[${user}][${home}]"
done | tr '\n' ';')
echo "U-32|${U32:-NONE}"

# U-33: 숨겨진 파일 및 디렉토리 검색 및 제거
U33_FILES=$(find / -maxdepth 4 -name '.*' -type f -not -path '/proc/*' -not -path '/sys/*' -not -path '/home/*' -not -path '/root/*' 2>/dev/null | head -10 | tr '\n' ';')
U33_DIRS=$(find / -maxdepth 4 -name '.*' -type d -not -path '/proc/*' -not -path '/sys/*' 2>/dev/null | head -10 | tr '\n' ';')
echo "U-33|HIDDEN_FILES=${U33_FILES:-NONE} HIDDEN_DIRS=${U33_DIRS:-NONE}"

# ── 3. 서비스 관리 ────────────────────────────────────────────────────────────

# U-34: Finger 서비스 비활성화
U34_PROC=$(ps -ef 2>/dev/null | grep finger | grep -v grep)
U34_XINETD=$(ls /etc/xinetd.d/ 2>/dev/null | grep -i finger)
echo "U-34|PROCESS=${U34_PROC:-NOT_RUNNING} XINETD=${U34_XINETD:-NOT_FOUND}"

# U-35: 공유 서비스에 대한 익명 접근 제한 (Anonymous FTP)
U35_FTP_PROC=$(ps -ef 2>/dev/null | grep -E '\bvsftpd\b|\bproftpd\b|\bpure-ftpd\b' | grep -v grep)
U35_ANON_FTP=$(grep -i 'anonymous_enable' /etc/vsftpd.conf /etc/vsftpd/vsftpd.conf 2>/dev/null | grep -v '^#')
U35_ANON_PROFTPD=$(grep -i 'allowoverwrite\|anonymous' /etc/proftpd.conf /etc/proftpd/proftpd.conf 2>/dev/null | grep -v '^#' | head -2 | tr '\n' ';')
echo "U-35|FTP_PROC=${U35_FTP_PROC:-NOT_RUNNING} ANON_FTP=${U35_ANON_FTP:-NOT_FOUND} PROFTPD=${U35_ANON_PROFTPD:-NOT_FOUND}"

# U-36: r 계열 서비스 비활성화
U36_PROC=$(ps -ef 2>/dev/null | grep -E '\b(rsh|rlogin|rexec)\b' | grep -v grep)
U36_XINETD=$(ls /etc/xinetd.d/ 2>/dev/null | grep -E 'rsh|rlogin|rexec')
echo "U-36|PROCESS=${U36_PROC:-NOT_RUNNING} XINETD=${U36_XINETD:-NOT_FOUND}"

# U-37: crontab 설정파일 권한 설정
U37_ALLOW=$(ls -l /etc/cron.allow 2>/dev/null | awk '{print $1, $3, $4}')
U37_DENY=$(ls -l /etc/cron.deny 2>/dev/null | awk '{print $1, $3, $4}')
U37_CRONTAB=$(ls -l /etc/crontab 2>/dev/null | awk '{print $1, $3, $4}')
U37_CRON_D=$(ls -al /etc/cron.d/ 2>/dev/null | awk '{print $1,$3,$4,$9}' | grep -v '^total\|^d\.\.' | tr '\n' ';')
echo "U-37|CRON_ALLOW=${U37_ALLOW:-NOT_FOUND} CRON_DENY=${U37_DENY:-NOT_FOUND} CRONTAB=${U37_CRONTAB:-NOT_FOUND} CRON_D=${U37_CRON_D:-NOT_FOUND}"

# U-38: DoS 공격에 취약한 서비스 비활성화
U38_PROC=$(ps -ef 2>/dev/null | grep -E '\b(echo|discard|daytime|chargen)\b' | grep -v grep)
U38_XINETD=$(ls /etc/xinetd.d/ 2>/dev/null | grep -E 'echo|discard|daytime|chargen')
echo "U-38|PROCESS=${U38_PROC:-NOT_RUNNING} XINETD=${U38_XINETD:-NOT_FOUND}"

# U-39: 불필요한 NFS 서비스 비활성화
U39_PROC=$(ps -ef 2>/dev/null | grep -E '\b(nfsd|mountd)\b' | grep -v grep)
U39_STATUS=$(systemctl is-active nfs-server 2>/dev/null || systemctl is-active nfs 2>/dev/null || echo 'inactive')
echo "U-39|PROCESS=${U39_PROC:-NOT_RUNNING} STATUS=${U39_STATUS}"

# U-40: NFS 접근 통제
U40_PROC=$(ps -ef 2>/dev/null | grep -E '\b(nfsd|mountd)\b' | grep -v grep)
U40_EXPORTS=$(grep -v '^#' /etc/exports 2>/dev/null | grep -v '^$' | tr '\n' ';')
echo "U-40|PROCESS=${U40_PROC:-NOT_RUNNING} EXPORTS=${U40_EXPORTS:-EMPTY}"

# U-41: 불필요한 automountd 제거
U41_PROC=$(ps -ef 2>/dev/null | grep -E '\b(automount|autofs)\b' | grep -v grep)
U41_STATUS=$(systemctl is-active autofs 2>/dev/null || echo 'inactive')
echo "U-41|PROCESS=${U41_PROC:-NOT_RUNNING} STATUS=${U41_STATUS}"

# U-42: 불필요한 RPC 서비스 비활성화
U42_PROC=$(ps -ef 2>/dev/null | grep -E 'rpc\.(cmsd|ttdbserverd|statd|ypupdated|rquotad|pcnfsd|nisd)|sadmind|rusersd|walld|sprayd|rstatd|kcms_server|cachefsd|rexd' | grep -v grep)
echo "U-42|PROCESS=${U42_PROC:-NOT_RUNNING}"

# U-43: NIS, NIS+ 점검
U43_PROC=$(ps -ef 2>/dev/null | grep -E '\b(ypserv|ypbind|ypxfrd)\b' | grep -v grep)
U43_STATUS=$(systemctl is-active ypbind 2>/dev/null || echo 'inactive')
echo "U-43|PROCESS=${U43_PROC:-NOT_RUNNING} STATUS=${U43_STATUS}"

# U-44: tftp, talk 서비스 비활성화
U44_PROC=$(ps -ef 2>/dev/null | grep -E '\b(tftp|talk|ntalk)\b' | grep -v grep)
U44_XINETD=$(ls /etc/xinetd.d/ 2>/dev/null | grep -E 'tftp|talk|ntalk')
echo "U-44|PROCESS=${U44_PROC:-NOT_RUNNING} XINETD=${U44_XINETD:-NOT_FOUND}"

# U-45: 메일 서비스 버전 점검 (Sendmail/Postfix)
U45_SENDMAIL_PROC=$(ps -ef 2>/dev/null | grep sendmail | grep -v grep)
U45_POSTFIX_PROC=$(ps -ef 2>/dev/null | grep postfix | grep -v grep)
U45_SENDMAIL_VER=$(sendmail -d0.1 -bv root 2>/dev/null | grep -i version | head -1)
U45_POSTFIX_VER=$(postconf -d mail_version 2>/dev/null | head -1)
echo "U-45|SENDMAIL=${U45_SENDMAIL_PROC:-NOT_RUNNING} POSTFIX=${U45_POSTFIX_PROC:-NOT_RUNNING} SENDMAIL_VER=${U45_SENDMAIL_VER:-NOT_FOUND} POSTFIX_VER=${U45_POSTFIX_VER:-NOT_FOUND}"

# U-46: 일반 사용자의 메일 서비스 실행 방지
U46_SENDMAIL_PROC=$(ps -ef 2>/dev/null | grep sendmail | grep -v grep)
U46_RESTRICT=$(grep -i 'RestrictQueueRun\|restrictqrun' /etc/mail/sendmail.cf 2>/dev/null | head -1)
U46_POSTFIX_OWNER=$(ls -l /usr/sbin/postfix 2>/dev/null | awk '{print $1, $3, $4}')
echo "U-46|SENDMAIL=${U46_SENDMAIL_PROC:-NOT_RUNNING} RESTRICT=${U46_RESTRICT:-NOT_FOUND} POSTFIX_PERM=${U46_POSTFIX_OWNER:-NOT_FOUND}"

# U-47: 스팸 메일 릴레이 제한
U47_SENDMAIL_PROC=$(ps -ef 2>/dev/null | grep sendmail | grep -v grep)
U47_CF=$(grep -i 'Drelay\|O DaemonPortOptions' /etc/mail/sendmail.cf 2>/dev/null | head -3 | tr '\n' ';')
U47_POSTFIX=$(grep -i 'smtpd_recipient_restrictions\|mynetworks' /etc/postfix/main.cf 2>/dev/null | head -3 | tr '\n' ';')
echo "U-47|SENDMAIL=${U47_SENDMAIL_PROC:-NOT_RUNNING} SENDMAIL_CF=${U47_CF:-NOT_FOUND} POSTFIX=${U47_POSTFIX:-NOT_FOUND}"

# U-48: expn, vrfy 명령어 제한
U48_SENDMAIL_PROC=$(ps -ef 2>/dev/null | grep sendmail | grep -v grep)
U48_OPT=$(grep -iE 'noexpn|novrfy|PrivacyOptions' /etc/mail/sendmail.cf 2>/dev/null | head -2 | tr '\n' ';')
echo "U-48|SENDMAIL=${U48_SENDMAIL_PROC:-NOT_RUNNING} PRIVACY_OPT=${U48_OPT:-NOT_FOUND}"

# U-49: DNS 보안 버전 패치
U49_PROC=$(ps -ef 2>/dev/null | grep named | grep -v grep)
U49_VER=$(named -v 2>/dev/null | head -1)
echo "U-49|PROCESS=${U49_PROC:-NOT_RUNNING} VERSION=${U49_VER:-NOT_FOUND}"

# U-50: DNS Zone Transfer 설정
U50_PROC=$(ps -ef 2>/dev/null | grep named | grep -v grep)
U50_CONF=$(grep -i 'allow-transfer' /etc/named.conf /etc/bind/named.conf.options 2>/dev/null | head -3 | tr '\n' ';')
echo "U-50|PROCESS=${U50_PROC:-NOT_RUNNING} ALLOW_TRANSFER=${U50_CONF:-NOT_FOUND}"

# U-51: DNS 서비스의 취약한 동적 업데이트 설정 금지
U51_PROC=$(ps -ef 2>/dev/null | grep named | grep -v grep)
U51_UPDATE=$(grep -i 'allow-update' /etc/named.conf /etc/bind/named.conf.options 2>/dev/null | head -3 | tr '\n' ';')
echo "U-51|PROCESS=${U51_PROC:-NOT_RUNNING} ALLOW_UPDATE=${U51_UPDATE:-NOT_FOUND}"

# U-52: Telnet 서비스 비활성화
U52_PROC=$(ps -ef 2>/dev/null | grep -E '\btelnetd?\b' | grep -v grep)
U52_STATUS=$(systemctl is-active telnet 2>/dev/null || echo 'inactive')
U52_XINETD=$(ls /etc/xinetd.d/ 2>/dev/null | grep -i telnet)
U52_PORT=$(ss -tlnp 2>/dev/null | grep ':23 ' || netstat -tlnp 2>/dev/null | grep ':23 ')
echo "U-52|PROCESS=${U52_PROC:-NOT_RUNNING} STATUS=${U52_STATUS} XINETD=${U52_XINETD:-NOT_FOUND} PORT23=${U52_PORT:-NOT_LISTENING}"

# U-53: FTP 서비스 정보 노출 제한 (배너 설정)
U53_FTP_PROC=$(ps -ef 2>/dev/null | grep -E '\bvsftpd\b|\bproftpd\b' | grep -v grep)
U53_VSFTPD=$(grep -i 'ftpd_banner' /etc/vsftpd.conf /etc/vsftpd/vsftpd.conf 2>/dev/null | grep -v '^#' | head -1)
U53_PROFTPD=$(grep -i 'ServerIdent' /etc/proftpd.conf /etc/proftpd/proftpd.conf 2>/dev/null | grep -v '^#' | head -1)
echo "U-53|FTP_PROC=${U53_FTP_PROC:-NOT_RUNNING} VSFTPD_BANNER=${U53_VSFTPD:-NOT_SET} PROFTPD_IDENT=${U53_PROFTPD:-NOT_SET}"

# U-54: 암호화되지 않는 FTP 서비스 비활성화
U54_FTP_PROC=$(ps -ef 2>/dev/null | grep -E '\bvsftpd\b|\bproftpd\b|\bpure-ftpd\b' | grep -v grep)
U54_FTP_STATUS=$(systemctl is-active vsftpd 2>/dev/null || systemctl is-active proftpd 2>/dev/null || echo 'inactive')
U54_SSL=$(grep -i 'ssl_enable\|TLSEngine' /etc/vsftpd.conf /etc/vsftpd/vsftpd.conf /etc/proftpd.conf 2>/dev/null | grep -v '^#' | head -2 | tr '\n' ';')
echo "U-54|FTP_PROC=${U54_FTP_PROC:-NOT_RUNNING} STATUS=${U54_FTP_STATUS} SSL_SETTING=${U54_SSL:-NOT_FOUND}"

# U-55: FTP 계정 Shell 제한
U55_FTP_PROC=$(ps -ef 2>/dev/null | grep -E '\bvsftpd\b|\bproftpd\b' | grep -v grep)
U55_SHELL=$(grep '^ftp' /etc/passwd 2>/dev/null | awk -F: '{print $1":"$7}')
echo "U-55|FTP_PROC=${U55_FTP_PROC:-NOT_RUNNING} FTP_SHELL=${U55_SHELL:-NOT_FOUND}"

# U-56: FTP 서비스 접근 제어 설정
U56_FTP_PROC=$(ps -ef 2>/dev/null | grep -E '\bvsftpd\b|\bproftpd\b' | grep -v grep)
U56_USERLIST=$(grep -i 'userlist_enable\|userlist_file\|userlist_deny' /etc/vsftpd.conf /etc/vsftpd/vsftpd.conf 2>/dev/null | grep -v '^#' | tr '\n' ';')
U56_FTPUSERS=$(ls -l /etc/ftpusers /etc/vsftpd/ftpusers /etc/vsftpd.ftpusers 2>/dev/null | awk '{print $1,$3,$4,$9}' | tr '\n' ';')
echo "U-56|FTP_PROC=${U56_FTP_PROC:-NOT_RUNNING} USERLIST=${U56_USERLIST:-NOT_FOUND} FTPUSERS=${U56_FTPUSERS:-NOT_FOUND}"

# U-57: Ftpusers 파일 설정 (root 차단)
U57_FTP_PROC=$(ps -ef 2>/dev/null | grep -E '\bvsftpd\b|\bproftpd\b' | grep -v grep)
U57_ROOT=$(grep '^root' /etc/vsftpd/ftpusers /etc/ftpusers /etc/vsftpd.ftpusers 2>/dev/null | head -1)
echo "U-57|FTP_PROC=${U57_FTP_PROC:-NOT_RUNNING} ROOT_IN_FTPUSERS=${U57_ROOT:-NOT_FOUND}"

# U-58: 불필요한 SNMP 서비스 구동 점검
U58_PROC=$(ps -ef 2>/dev/null | grep snmpd | grep -v grep)
U58_STATUS=$(systemctl is-active snmpd 2>/dev/null || echo 'inactive')
echo "U-58|PROCESS=${U58_PROC:-NOT_RUNNING} STATUS=${U58_STATUS}"

# U-59: 안전한 SNMP 버전 사용 (v3 이상)
U59_PROC=$(ps -ef 2>/dev/null | grep snmpd | grep -v grep)
U59_V3=$(grep -E '^(createUser|rouser|rwuser)' /etc/snmp/snmpd.conf 2>/dev/null | head -3 | tr '\n' ';')
U59_V1V2=$(grep -E '^(rocommunity|rwcommunity|com2sec)' /etc/snmp/snmpd.conf 2>/dev/null | head -3 | tr '\n' ';')
echo "U-59|PROCESS=${U59_PROC:-NOT_RUNNING} V3_CONFIG=${U59_V3:-NOT_FOUND} V1V2_CONFIG=${U59_V1V2:-NOT_FOUND}"

# U-60: SNMP Community String 복잡성 설정
U60_PROC=$(ps -ef 2>/dev/null | grep snmpd | grep -v grep)
U60_COMM=$(grep -E '^(community|rocommunity|rwcommunity)' /etc/snmp/snmpd.conf 2>/dev/null | tr '\n' ';')
U60_WEAK=$(grep -Ei 'public|private' /etc/snmp/snmpd.conf 2>/dev/null | grep -v '^#' | tr '\n' ';')
echo "U-60|PROCESS=${U60_PROC:-NOT_RUNNING} COMMUNITY=${U60_COMM:-NOT_FOUND} WEAK_STRING=${U60_WEAK:-NONE}"

# U-61: SNMP Access Control 설정
U61_PROC=$(ps -ef 2>/dev/null | grep snmpd | grep -v grep)
U61_ACL=$(grep -E '^(com2sec|access|group|view|rocommunity|rwcommunity)' /etc/snmp/snmpd.conf 2>/dev/null | head -5 | tr '\n' ';')
echo "U-61|PROCESS=${U61_PROC:-NOT_RUNNING} ACL_CONFIG=${U61_ACL:-NOT_FOUND}"

# U-62: 로그인 시 경고 메시지 설정
U62_MOTD=$(cat /etc/motd 2>/dev/null | grep -v '^$' | head -3 | tr '\n' ';')
U62_ISSUE=$(cat /etc/issue 2>/dev/null | grep -v '^$' | head -2 | tr '\n' ';')
U62_ISSUE_NET=$(cat /etc/issue.net 2>/dev/null | grep -v '^$' | head -2 | tr '\n' ';')
U62_BANNER=$(grep -i '^Banner' /etc/ssh/sshd_config 2>/dev/null | grep -v '^#')
echo "U-62|MOTD=${U62_MOTD:-EMPTY} ISSUE=${U62_ISSUE:-EMPTY} ISSUE_NET=${U62_ISSUE_NET:-EMPTY} SSH_BANNER=${U62_BANNER:-NOT_SET}"

# U-63: sudo 명령어 접근 관리
U63_SUDOERS=$(ls -l /etc/sudoers 2>/dev/null | awk '{print $1, $3, $4}')
U63_CONTENT=$(grep -v '^#\|^$\|^Defaults' /etc/sudoers 2>/dev/null | grep -v '^%' | head -5 | tr '\n' ';')
U63_NOPASSWD=$(grep -i 'NOPASSWD' /etc/sudoers /etc/sudoers.d/* 2>/dev/null | grep -v '^#' | head -3 | tr '\n' ';')
echo "U-63|SUDOERS_PERM=${U63_SUDOERS:-NOT_FOUND} CONTENT=${U63_CONTENT:-NOT_FOUND} NOPASSWD=${U63_NOPASSWD:-NONE}"

# ── 4. 패치 관리 ────────────────────────────────────────────────────────────

# U-64: 주기적 보안 패치 및 벤더 권고사항 적용
U64_OS=$(grep PRETTY_NAME /etc/os-release 2>/dev/null | cut -d= -f2 | tr -d '"')
U64_KERNEL=$(uname -r 2>/dev/null)
U64_UPDATES=$(yum check-update 2>/dev/null | grep -c 'updates\|security' || apt list --upgradable 2>/dev/null | grep -c 'upgradable' || echo 'NOT_CHECKED')
echo "U-64|OS=${U64_OS:-NOT_FOUND} KERNEL=${U64_KERNEL:-NOT_FOUND} PENDING_UPDATES=${U64_UPDATES}"

# ── 5. 로그 관리 ────────────────────────────────────────────────────────────

# U-65: NTP 및 시각 동기화 설정
U65_NTP_STATUS=$(systemctl is-active ntpd 2>/dev/null || echo 'inactive')
U65_CHRONY_STATUS=$(systemctl is-active chronyd 2>/dev/null || echo 'inactive')
U65_NTP_CONF=$(grep '^server\|^pool' /etc/ntp.conf 2>/dev/null | head -3 | tr '\n' ';')
U65_CHRONY_CONF=$(grep '^server\|^pool' /etc/chrony.conf 2>/dev/null | head -3 | tr '\n' ';')
U65_SYNC=$(chronyc tracking 2>/dev/null | grep 'Reference ID\|Stratum' | head -2 | tr '\n' ';' || ntpq -pn 2>/dev/null | grep '^\*' | head -1)
echo "U-65|NTP_STATUS=${U65_NTP_STATUS} CHRONY_STATUS=${U65_CHRONY_STATUS} NTP_CONF=${U65_NTP_CONF:-NOT_FOUND} CHRONY_CONF=${U65_CHRONY_CONF:-NOT_FOUND} SYNC=${U65_SYNC:-NOT_SYNCED}"

# U-66: 정책에 따른 시스템 로깅 설정
U66_STATUS=$(systemctl is-active rsyslog 2>/dev/null || systemctl is-active syslog 2>/dev/null || echo 'inactive')
U66_CONF=$(grep -v '^ *#' /etc/rsyslog.conf 2>/dev/null | grep -E '^\*\.|^auth|^mail|^cron|messages|secure' | tr '\n' ';')
echo "U-66|STATUS=${U66_STATUS} CONF=${U66_CONF:-NOT_FOUND}"

# U-67: 로그 디렉터리 소유자 및 권한 설정
U67_VARLOG=$(ls -ald /var/log 2>/dev/null | awk '{print $1, $3, $4}')
U67_FILES=$(ls -l /var/log/ 2>/dev/null | awk '{print $1,$3,$4,$9}' | grep -v '^total\|^d' | awk -F' ' '$1~/[o][^r]/{print}' | head -5 | tr '\n' ';')
U67_BAD=$(find /var/log -type f ! -user root 2>/dev/null | head -5 | tr '\n' ';')
echo "U-67|VARLOG_PERM=${U67_VARLOG:-NOT_FOUND} BAD_PERM_FILES=${U67_FILES:-NONE} NON_ROOT_OWNED=${U67_BAD:-NONE}"

echo "===CCE_SCAN_END==="
