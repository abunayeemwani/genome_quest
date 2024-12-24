import json
from django.contrib.auth import login

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny

from .models import Mission, Puzzle, PuzzleSubmission
from .serializers import (
    MissionSerializer,
    PuzzleSerializer,
    PuzzleSubmissionSerializer,
    LoginSerializer,
    RegisterSerializer,
)


class LoginViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        login(request, user)
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'message': 'Successfully logged in'
        })


class RegisterViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        login(request, user)
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'message': 'Successfully registered and logged in'
        })


class MissionViewSet(viewsets.ModelViewSet):
    '''
    ViewSet for managing game missions.

    GET /missions/
        Request: None
        Response: List[Mission]

    POST /missions/
        Request:
            - title: str
            - description: str
            - status: str (optional)
        Response: Mission
    '''

    queryset = Mission.objects.all()
    serializer_class = MissionSerializer

    @action(detail=True, methods=['get'])
    def start(self, request, pk=None):
        mission = self.get_object()
        if mission.status != 'pending':
            return Response(
                {'error': 'Mission already started or completed'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        mission.status = 'in_progress'
        mission.save()
        return Response(
            {'message': 'Mission started'},
            status=status.HTTP_200_OK,
        )


class PuzzleViewSet(viewsets.ModelViewSet):
    '''
    ViewSet for managing game puzzles.

    GET /puzzles/?mission_id={id}
        Request:
            Query Params:
                - mission_id: int
        Response: List[Puzzle]

    POST /puzzles/
        Request:
            - mission_id: int
            - title: str
            - sequence_data: str
            - mutation_data: List[int]
            [4,8,5,2]
        Response: Puzzle
    '''

    serializer_class = PuzzleSerializer

    def get_queryset(self):
        mission_id = self.request.query_params.get('mission_id')
        if mission_id:
            return Puzzle.objects.filter(mission_id=mission_id)
        return Puzzle.objects.none()


class PuzzleSubmissionViewSet(viewsets.ModelViewSet):
    '''
    ViewSet for managing puzzle submissions.

    GET /puzzle-submissions/
        Request: None
        Response: List[PuzzleSubmission]

    POST /puzzle-submissions/
        Request:
            - mission: int
            - puzzle: int
            - mutations_found: List[int]
            [6,9,3,2]
        Response: PuzzleSubmission
    '''

    serializer_class = PuzzleSubmissionSerializer

    def get_queryset(self):
        return PuzzleSubmission.objects.all()

    def create(self, request, *args, **kwargs):
        mission_id = request.data.get('mission')
        puzzle_id = request.data.get('puzzle')
        mission = Mission.objects.get(id=mission_id)
        puzzle = Puzzle.objects.get(id=puzzle_id)

        if mission.status != 'in_progress':
            return Response(
                {'error': 'Mission is not in progress'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        mutations_found = json.loads(request.data.get('mutations_found', '[]'))

        correct_mutations = set(puzzle.mutation_data)
        submitted_mutations = set(mutations_found)

        correct_answers = correct_mutations.intersection(submitted_mutations)
        missed_mutations = correct_mutations - submitted_mutations
        false_positives = submitted_mutations - correct_mutations

        puzzle.status = 'completed'
        puzzle.save()

        total_mutations = len(correct_mutations)
        correct_count = len(correct_answers)
        accuracy = (
            correct_count / total_mutations * 100
            if total_mutations > 0 else 0
        )

        serializer = self.get_serializer(
            data={
                'mission': mission_id,
                'puzzle': puzzle_id,
                'mutations_found': mutations_found,
                'score': correct_count,
            },
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        total_puzzles = Puzzle.objects.filter(mission=mission).count()
        completed_puzzles = PuzzleSubmission.objects.filter(
            mission=mission,
        ).count()

        if completed_puzzles == total_puzzles:
            mission.status = 'completed'
            mission.save()

        headers = self.get_success_headers(serializer.data)

        response_data = {
            'accuracy': round(accuracy, 2),
            'score': {
                'correct_mutations': list(correct_answers),
                'missed_mutations': list(missed_mutations),
                'incorrect_mutations': list(false_positives),
                'total_mutations': total_mutations,
                'found_mutations': len(submitted_mutations)
            },
            'feedback': self.generate_feedback(accuracy)
        }

        return Response(
            response_data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def generate_feedback(self, accuracy):
        if accuracy >= 90:
            return "Excellent! You found almost all mutations!"
        elif accuracy >= 70:
            return "Good job! Keep practicing to improve further."
        elif accuracy >= 50:
            return "You're making progress."
        else:
            return "Keep practicing. Focus on analyzing the sequence."
