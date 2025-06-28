from django.urls import path # type: ignore
from .views import handle_request, generate_unique, delete_database, delete_chat, visualize_code, update_name

urlpatterns = [
    path('', handle_request, name = 'bot_page'),
    path('unique_chat' ,generate_unique ,name = 'unique_chat_creator'),
    path('delete_database', delete_database, name = 'database_destruction'),
    path('delete_chat', delete_chat, name="chat_delete"),
    path('tree_parser', visualize_code, name="tree_parser"),
    path('change_name', update_name, name= 'update_name')
]