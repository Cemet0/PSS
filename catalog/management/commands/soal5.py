import time

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection
from django.test.utils import CaptureQueriesContext

from catalog.models import Course, Lesson, Enrollment, Assignment, Submission
from users.models import User


def judul(teks):
    print("\n" + "=" * 60)
    print(teks)
    print("=" * 60)


def ukur(fungsi):
    """Jalankan fungsi, kembalikan (jumlah_data, jumlah_query, waktu_detik)."""
    awal = time.perf_counter()
    with CaptureQueriesContext(connection) as ctx:
        n = fungsi()
    waktu = time.perf_counter() - awal
    return n, len(ctx.captured_queries), waktu


class Command(BaseCommand):
    help = "Soal 5 UTS: siapkan dataset lalu ukur optimasi query"

    def handle(self, *args, **options):
        # ---------- Persiapan data (aman diulang, tanpa duplikat) ----------
        judul("PERSIAPAN DATA")
        call_command("generate_performance_data")
        call_command("generate_relationship_data")

        print("\nJumlah data pengujian:")
        print("Lecturer  :", User.objects.filter(role="LECTURER").count())
        print("Student   :", User.objects.filter(role="STUDENT").count())
        print("Course    :", Course.objects.count())
        print("Lesson    :", Lesson.objects.count())
        print("Enrollment:", Enrollment.objects.count())
        print("Assignment:", Assignment.objects.count())
        print("Submission:", Submission.objects.count())

        # ---------- 5a. Course + Lecturer tanpa select_related ----------
        judul("5a. Course + Lecturer TANPA select_related()")

        def tanpa_select():
            qs = Course.objects.filter(code__startswith="PERF").order_by("code")[:100]
            return len([(c.title, c.lecturer.username) for c in qs])

        n_a, q_a, t_a = ukur(tanpa_select)
        print(f"Course: {n_a} | Query: {q_a} | Waktu: {t_a:.4f} detik")

        # ---------- 5b. Dengan select_related ----------
        judul('5b. Course + Lecturer DENGAN select_related("lecturer")')

        def dengan_select():
            qs = (
                Course.objects.filter(code__startswith="PERF")
                .order_by("code")
                .select_related("lecturer")[:100]
            )
            return len([(c.title, c.lecturer.username) for c in qs])

        n_b, q_b, t_b = ukur(dengan_select)
        print(f"Course: {n_b} | Query: {q_b} | Waktu: {t_b:.4f} detik")
        print(f"Perbandingan query: {q_a} -> {q_b}")

        # ---------- 5c. Course + Lesson ----------
        judul("5c. Course + Lesson: tanpa vs dengan prefetch_related()")

        def tanpa_prefetch():
            qs = Course.objects.filter(code__startswith="PERF").order_by("code")[:50]
            return len([[l.title for l in c.lessons.all()] for c in qs])

        def dengan_prefetch():
            qs = (
                Course.objects.filter(code__startswith="PERF")
                .order_by("code")
                .prefetch_related("lessons")[:50]
            )
            return len([[l.title for l in c.lessons.all()] for c in qs])

        n_c1, q_c1, t_c1 = ukur(tanpa_prefetch)
        n_c2, q_c2, t_c2 = ukur(dengan_prefetch)
        print(f"BEFORE (tanpa)   : Course {n_c1} | Query {q_c1} | {t_c1:.4f} detik")
        print(f"AFTER (prefetch) : Course {n_c2} | Query {q_c2} | {t_c2:.4f} detik")

        # ---------- 5d. EXPLAIN ----------
        judul("5d. QuerySet.explain()")
        print("\n[Query 1] Course.objects.filter(code='PERF05000')")
        print(Course.objects.filter(code="PERF05000").explain())

        print("\n[Query 2] Course.objects.filter(is_active=True, title='Performance Course 5000')")
        print(Course.objects.filter(is_active=True, title="Performance Course 5000").explain())

        # ---------- Ringkasan tabel untuk laporan ----------
        judul("TABEL HASIL (salin ke laporan)")
        print(f"{'Skenario':<20}{'Jumlah Data':<14}{'Query Sebelum':<16}{'Query Sesudah'}")
        print(f"{'Course + Lecturer':<20}{n_a:<14}{q_a:<16}{q_b}")
        print(f"{'Course + Lesson':<20}{n_c1:<14}{q_c1:<16}{q_c2}")
        print(f"\nWaktu Course+Lecturer : {t_a:.4f} s -> {t_b:.4f} s")
        print(f"Waktu Course+Lesson   : {t_c1:.4f} s -> {t_c2:.4f} s")