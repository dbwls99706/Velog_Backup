from github import Github, GithubException
from typing import Optional, List
import base64
from datetime import datetime


class GitHubService:
    """GitHub API 서비스"""

    def __init__(self, access_token: str):
        self.client = Github(access_token)
        self.user = self.client.get_user()

    def create_or_get_repo(self, repo_name: str = "velog-backup") -> dict:
        """저장소 생성 또는 가져오기"""
        try:
            # 이미 존재하는지 확인
            repo = self.user.get_repo(repo_name)
            return {
                "name": repo.name,
                "url": repo.html_url,
                "full_name": repo.full_name
            }
        except GithubException as e:
            if e.status == 404:
                # 저장소가 없으면 생성
                repo = self.user.create_repo(
                    name=repo_name,
                    description="Velog 포스트 자동 백업 저장소",
                    private=False,
                    auto_init=True  # README.md 자동 생성
                )
                return {
                    "name": repo.name,
                    "url": repo.html_url,
                    "full_name": repo.full_name
                }
            else:
                raise

    def upload_or_update_file(
        self,
        repo_name: str,
        file_path: str,
        content: str,
        commit_message: Optional[str] = None
    ) -> bool:
        """파일 업로드 또는 업데이트"""
        try:
            repo = self.user.get_repo(repo_name)

            if commit_message is None:
                commit_message = f"Update {file_path}"

            try:
                # 파일이 이미 존재하는지 확인
                existing_file = repo.get_contents(file_path)
                # 파일 업데이트
                repo.update_file(
                    path=file_path,
                    message=commit_message,
                    content=content,
                    sha=existing_file.sha
                )
            except GithubException as e:
                if e.status == 404:
                    # 파일이 없으면 새로 생성
                    repo.create_file(
                        path=file_path,
                        message=commit_message,
                        content=content
                    )
                else:
                    raise

            return True

        except Exception as e:
            print(f"Error uploading file to GitHub: {e}")
            return False

    def delete_file(self, repo_name: str, file_path: str) -> bool:
        """파일 삭제"""
        try:
            repo = self.user.get_repo(repo_name)
            file = repo.get_contents(file_path)

            repo.delete_file(
                path=file_path,
                message=f"Delete {file_path}",
                sha=file.sha
            )
            return True

        except Exception as e:
            print(f"Error deleting file from GitHub: {e}")
            return False

    def list_files(self, repo_name: str, path: str = "") -> List[dict]:
        """저장소 내 파일 목록 조회"""
        try:
            repo = self.user.get_repo(repo_name)
            contents = repo.get_contents(path)

            files = []
            for content in contents:
                if content.type == "file":
                    files.append({
                        "name": content.name,
                        "path": content.path,
                        "sha": content.sha,
                        "size": content.size
                    })

            return files

        except Exception as e:
            print(f"Error listing files from GitHub: {e}")
            return []

    def get_user_info(self) -> dict:
        """사용자 정보 조회"""
        return {
            "username": self.user.login,
            "name": self.user.name,
            "email": self.user.email
        }

    def create_readme(self, repo_name: str):
        """README.md 생성"""
        readme_content = f"""# Velog 백업 저장소

이 저장소는 Velog 포스트를 자동으로 백업한 저장소입니다.

- 백업 시작일: {datetime.now().strftime('%Y-%m-%d')}
- 자동 백업 시스템을 통해 관리됩니다.

## 구조

각 포스트는 Markdown 형식으로 저장되며, frontmatter에 메타데이터가 포함됩니다.

## 백업 정보

- 정기 백업이 자동으로 수행됩니다.
- 포스트 수정 시 자동으로 업데이트됩니다.
"""

        try:
            self.upload_or_update_file(
                repo_name=repo_name,
                file_path="README.md",
                content=readme_content,
                commit_message="Initialize Velog backup repository"
            )
        except Exception as e:
            print(f"Error creating README: {e}")
