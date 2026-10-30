from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from users.models import User
from catalog.models import Course, Lesson, Enrollment, Assignment, Submission


def judul(teks):
    print("\n" + "=" * 60)
    print(teks)
    print("=" * 60)


class Command(BaseCommand):
    help = "Soal 4 UTS: siapkan data minimal (4a), query (4b), demo get/filter/all (4d)"

    def handle(self, *args, **options):
        self.soal_4a()
        self.soal_4b()
        self.soal_4d()

    # ------------------------------------------------------------------
    # 4a. Data minimal (aman dijalankan berulang, tidak membuat duplikat)
    # ------------------------------------------------------------------
    def soal_4a(self):
        judul("4a. PASTIKAN DATA MINIMAL")

        def buat_user(username, email, role):
            user = User.objects.filter(username=username).first()
            if user is None:
                user = User.objects.create_user(
                    username=username, email=email, password="12345", role=role
                )
            return user

        dosen = buat_user("suprayogi", "suprayogi@gmail.com", User.Role.LECTURER)
        mhs1 = buat_user("fauzan", "fauzan@gmail.com", User.Role.STUDENT)
        mhs2 = buat_user("mahasiswa2", "mhs2@gmail.com", User.Role.STUDENT)

        c1, _ = Course.objects.get_or_create(
            code="PSS01",
            defaults={"title": "Pemrograman Sisi Server", "lecturer": dosen},
        )
        Course.objects.get_or_create(
            code="PSS02",
            defaults={"title": "Django Framework", "lecturer": dosen},
        )

        materi = [
            (1, "Pengenalan Backend"),
            (2, "Pola Arsitektur Backend"),
            (3, "Containerisasi dengan Docker"),
        ]
        for order, title in materi:
            Lesson.objects.get_or_create(
                course=c1,
                order=order,
                defaults={"title": title, "content": f"Materi {order}"},
            )

        Enrollment.objects.get_or_create(student=mhs1, course=c1)
        Enrollment.objects.get_or_create(student=mhs2, course=c1)

        tugas, _ = Assignment.objects.get_or_create(
            course=c1,
            title="Tugas Django ORM",
            defaults={
                "description": "Implementasi model dan relationship Django ORM.",
                "deadline": timezone.now() + timedelta(days=7),
            },
        )
        Submission.objects.get_or_create(
            assignment=tugas,
            student=mhs1,
            defaults={"content": "Jawaban saya", "grade": 87.5},
        )

        print("Dosen        :", User.objects.filter(role="LECTURER").count(), "(min 1)")
        print("Mahasiswa    :", User.objects.filter(role="STUDENT").count(), "(min 2)")
        print("Course       :", Course.objects.count(), "(min 2)")
        print("Lesson PSS01 :", Lesson.objects.filter(course=c1).count(), "(min 3)")
        print("Enrollment   :", Enrollment.objects.count(), "(min 2)")
        print("Assignment   :", Assignment.objects.count(), "(min 1)")
        print("Submission   :", Submission.objects.count(), "(min 1)")

    # ------------------------------------------------------------------
    # 4b. Enam query
    # ------------------------------------------------------------------
    def soal_4b(self):
        judul("4b. ENAM QUERY")

        course = Course.objects.get(code="PSS01")
        dosen = User.objects.get(username="suprayogi")
        tugas = Assignment.objects.get(course=course, title="Tugas Django ORM")

        print("\n[1] Semua Course beserta kode dan judul (10 pertama)")
        for row in Course.objects.values("code", "title")[:10]:
            print("   ", row)
        print("    Total:", Course.objects.count())

        print("\n[2] Course yang diampu seorang dosen (suprayogi)")
        for row in Course.objects.filter(lecturer=dosen).values("code", "title")[:10]:
            print("   ", row)
        print("    Total:", Course.objects.filter(lecturer=dosen).count())

        print("\n[3] Semua Lesson milik Course PSS01")
        for row in Lesson.objects.filter(course=course).values("order", "title"):
            print("   ", row)

        print("\n[4] Jumlah mahasiswa terdaftar pada Course PSS01")
        print("    ", Enrollment.objects.filter(course=course).count())

        print("\n[5] Semua Assignment milik Course PSS01")
        for row in Assignment.objects.filter(course=course).values("title", "deadline"):
            print("   ", row)

        print("\n[6] Semua Submission milik Assignment 'Tugas Django ORM'")
        for row in Submission.objects.filter(assignment=tugas).values(
            "student__username", "content", "grade"
        ):
            print("   ", row)

    # ------------------------------------------------------------------
    # 4d. Demo get / filter / all
    # ------------------------------------------------------------------
    def soal_4d(self):
        judul("4d. DEMO get(), filter(), all()")

        print("\nget()    ->", Course.objects.get(code="PSS01"))
        print("filter() ->", Course.objects.filter(code__startswith="PSS").count(), "course berkode PSS*")
        print("all()    ->", Course.objects.all().count(), "course (semua)")

        print("\nget() pada data yang tidak ada:")
        try:
            Course.objects.get(code="TIDAKADA")
        except Course.DoesNotExist as e:
            print("    DoesNotExist:", e)

        print("filter() pada data yang tidak ada:")
        print("    ", Course.objects.filter(code="TIDAKADA"), "(kosong, tidak error)")