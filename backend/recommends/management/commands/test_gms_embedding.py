from django.core.management.base import BaseCommand

from recommends.engine import embed_texts


class Command(BaseCommand):
    help = "GMS 임베딩 엔드포인트 연결 테스트 (성공/실패 콘솔 출력)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--text",
            type=str,
            default="health check",
            help="임베딩할 테스트 텍스트 (기본: health check)",
        )

    def handle(self, *args, **options):
        text = options["text"]
        try:
            embeddings = embed_texts([text])
            if embeddings and embeddings[0]:
                self.stdout.write(self.style.SUCCESS("임베딩 성공 (응답 수신)"))
                self.stdout.write(f"- 벡터 길이: {len(embeddings[0])}")
            else:
                self.stdout.write(self.style.WARNING("응답은 받았지만 벡터가 비었습니다."))
        except Exception as exc:  # 네트워크/키 오류 등
            self.stderr.write(self.style.ERROR(f"임베딩 실패: {exc}"))
