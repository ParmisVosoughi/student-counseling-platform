from rest_framework.routers import DefaultRouter
from .views import StudentViewSet,WeeklyPerformanceViewSet,AssessmentResultViewSet,StudentChallengeViewSet,ProgramLogicCategoryViewSet,ProgramLogicReviewViewSet,ActivityViewSet
router=DefaultRouter()
router.register('students',StudentViewSet,basename='student')
router.register('weekly-performance',WeeklyPerformanceViewSet,basename='weekly-performance')
router.register('assessment-results',AssessmentResultViewSet,basename='assessment-result')
router.register('challenges',StudentChallengeViewSet,basename='challenge')
router.register('program-review-categories',ProgramLogicCategoryViewSet,basename='program-review-category')
router.register('program-reviews',ProgramLogicReviewViewSet,basename='program-review')
router.register('activities',ActivityViewSet,basename='activity')
urlpatterns=router.urls
