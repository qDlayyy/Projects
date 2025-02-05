import string
import random
from django.core.management.base import BaseCommand
from api.models import StoreBase, Promocodes


class Command(BaseCommand):
    def handle(self, *args, **options):
        '''
            Creation of the default nessesary model items
        '''

        def new_promocode(length=6):
            if length > 6 or length <= 0:
                length = 6
            possible_charactares = string.ascii_uppercase + string.ascii_lowercase + string.digits
            
            return ''.join(random.choice(possible_charactares) for _ in range(length))

        def new_sale_percentage():
            return random.randint(5, 20)
        
        def promocode_generator(amount):
        
            for _ in range(amount):
                code = new_promocode()
                sale_percentage = new_sale_percentage()
                is_active = random.choice([True, False])
                summarizes_with_other_sales = random.choice([True, False])

                yield{
                    'code': code,
                    'sale_percentage': sale_percentage,
                    'is_active': is_active,
                    'summarizes_with_other_sales': summarizes_with_other_sales
                }


        if StoreBase.objects.count() == 0:
            StoreBase.objects.create()
        
        for generated_promocode_dict in promocode_generator(5):
            Promocodes.objects.create(** generated_promocode_dict)
        

    


