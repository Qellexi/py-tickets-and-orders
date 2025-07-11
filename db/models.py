from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import UniqueConstraint
from django.conf import settings
from django.core.exceptions import ValidationError


class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name


class Actor(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    actors = models.ManyToManyField(to=Actor, related_name="movies")
    genres = models.ManyToManyField(to=Genre, related_name="movies")

    class Meta:
        indexes = [
            models.Index(fields=["title"]),
        ]
    
    def __str__(self) -> str:
        return self.title


class CinemaHall(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self) -> str:
        return self.name


class MovieSession(models.Model):
    show_time = models.DateTimeField()
    cinema_hall = models.ForeignKey(
        to=CinemaHall, on_delete=models.CASCADE, related_name="movie_sessions"
    )
    movie = models.ForeignKey(
        to=Movie, on_delete=models.CASCADE, related_name="movie_sessions"
    )

    def __str__(self) -> str:
        return f"{self.movie.title} {str(self.show_time)}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    class Meta:
        ordering = ["-created_at"] #desc
    def __str__(self) -> str:
        return f"Order: {self.created_at}"


class Ticket(models.Model):
    movie_session = models.ForeignKey("MovieSession", on_delete=models.CASCADE)
    order = models.ForeignKey("Order", on_delete=models.CASCADE)
    row = models.IntegerField();
    seat = models.IntegerField();

    class Meta:
        constraints = [
            UniqueConstraint(fields=["seat", "row", "movie_session"], name="unique_ticket")
        ]
    def clean(self):
        if not (1 <= self.seat <= self.movie_session.cinema_hall.seats_in_row):
            raise ValidationError({"seat": f"seat must be in range (1, {self.movie_session.cinema_hall.seats_in_row}), not {self.seat}"})
        if not (1 <= self.row <= self.movie_session.cinema_hall.rows):
            raise ValidationError({"row": f"row must be in range (1, {self.movie_session.cinema_hall.rows}), not {self.row}"})
            
    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
        
    def __str__(self):
        return f"Ticket: {self.movie_session} (row: {self.row}, seat: {self.seat})"
        


class User(AbstractUser):
    pass
