from django.db import models
from django.contrib.auth.models import AbstractUser


class Player(AbstractUser):
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class Mission(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=(
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
        ),
        default='pending',
    )

    def __str__(self):
        return self.name


class Puzzle(models.Model):
    mission = models.ForeignKey(
        Mission,
        on_delete=models.CASCADE,
        related_name='puzzles',
    )
    sequence_data = models.TextField()
    mutation_data = models.JSONField(default=list)
    status = models.CharField(
        max_length=20,
        choices=(
            ('pending', 'Pending'),
            ('completed', 'Completed'),
        ),
        default='pending',
    )
    time_limit = models.IntegerField(
        help_text="Time limit in seconds to complete the puzzle",
        default=120,
    )

    def __str__(self):
        return f'Puzzle - {self.id}'


class PuzzleSubmission(models.Model):
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    mission = models.ForeignKey(
        Mission,
        on_delete=models.CASCADE,
    )
    puzzle = models.ForeignKey(
        Puzzle,
        on_delete=models.CASCADE,
    )
    mutations_found = models.JSONField(default=list)
    timestamp = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f'Puzzle Submission - {self.id}'
