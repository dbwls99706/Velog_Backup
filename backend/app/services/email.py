import httpx
import logging
from typing import Optional
from datetime import datetime, timezone

from app.core.config import settings

logger = logging.getLogger(__name__)

RESEND_API_URL = "https://api.resend.com/emails"


class EmailService:
    """Resend 기반 이메일 알림 서비스"""

    @staticmethod
    def send_backup_notification(
        to_email: str,
        username: str,
        posts_new: int,
        posts_updated: int,
        posts_failed: int,
        total_posts: int,
        status: str = "success",
        error_message: Optional[str] = None
    ):
        """백업 완료/실패 알림 이메일 발송 (Resend API)"""
        api_key = settings.RESEND_API_KEY

        if not api_key:
            logger.warning("RESEND_API_KEY not configured, skipping email notification")
            return

        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        if status == "success":
            subject = f"[Velog Backup] @{username} 백업 완료"
            html = f"""
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: #525252; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                    <h1 style="margin: 0; font-size: 20px;">Velog Backup</h1>
                </div>
                <div style="background: #f9fafb; padding: 24px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 8px 8px;">
                    <h2 style="color: #1f2937; margin-top: 0;">백업이 완료되었습니다</h2>
                    <p style="color: #6b7280;">@{username} 계정의 백업 결과입니다.</p>

                    <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
                        <tr>
                            <td style="padding: 8px 16px; background: white; border: 1px solid #e5e7eb;">새 포스트</td>
                            <td style="padding: 8px 16px; background: white; border: 1px solid #e5e7eb; font-weight: bold;">{posts_new}개</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 16px; background: white; border: 1px solid #e5e7eb;">업데이트</td>
                            <td style="padding: 8px 16px; background: white; border: 1px solid #e5e7eb; font-weight: bold;">{posts_updated}개</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 16px; background: white; border: 1px solid #e5e7eb;">실패</td>
                            <td style="padding: 8px 16px; background: white; border: 1px solid #e5e7eb; font-weight: bold; color: {'#dc2626' if posts_failed > 0 else '#1f2937'};">{posts_failed}개</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 16px; background: white; border: 1px solid #e5e7eb;">전체 포스트</td>
                            <td style="padding: 8px 16px; background: white; border: 1px solid #e5e7eb; font-weight: bold;">{total_posts}개</td>
                        </tr>
                    </table>

                    <p style="color: #9ca3af; font-size: 12px; margin-top: 16px;">{now}</p>
                </div>
            </div>
            """
        else:
            subject = f"[Velog Backup] @{username} 백업 실패"
            error_html = ""
            if error_message:
                safe_error = error_message[:500].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                error_html = f'<div style="background: #fef2f2; border: 1px solid #fecaca; padding: 12px; border-radius: 4px; margin: 16px 0;"><pre style="margin: 0; white-space: pre-wrap; font-size: 13px; color: #991b1b;">{safe_error}</pre></div>'
            html = f"""
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: #dc2626; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                    <h1 style="margin: 0; font-size: 20px;">Velog Backup</h1>
                </div>
                <div style="background: #f9fafb; padding: 24px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 8px 8px;">
                    <h2 style="color: #dc2626; margin-top: 0;">백업에 실패했습니다</h2>
                    <p style="color: #6b7280;">@{username} 계정의 백업 중 오류가 발생했습니다.</p>

                    {error_html}

                    <p style="color: #6b7280;">대시보드에서 다시 시도해주세요.</p>
                    <p style="color: #9ca3af; font-size: 12px; margin-top: 16px;">{now}</p>
                </div>
            </div>
            """

        try:
            response = httpx.post(
                RESEND_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": "Velog Backup <onboarding@resend.dev>",
                    "to": [to_email],
                    "subject": subject,
                    "html": html,
                },
                timeout=10,
            )
            response.raise_for_status()
            logger.info(f"Backup notification email sent to {to_email}")
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
