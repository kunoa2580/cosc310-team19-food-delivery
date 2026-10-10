from pathlib import Path
import json
from typing import List, Dict, Any


class MenuItemRepository:
    """ This class is for loading and saving updated data back the json file (DATABASE)
     branch: feature/menu-item-schema

     @TheTureFADED

    """

    def __init__(self):
        """Defined where is the data path   
        branch: feature/menu-item-schema
        
        @TheTureFADED
        
        """
        
        self.DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "menu_items.json"

    def load_all_items(self) -> List[Dict[str, Any]]:
        """ Loading all of menu_item and return it as List of dictionary 
        
        branch: feature/menu-item-schema
        
        @TheTureFADED
        
        """
        if not self.DATA_PATH.exists():
            return []
        with self.DATA_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)

    def save_all_items(self, menu_items: List[Dict[str, Any]]) -> None:
        """  write back all of updated menu item back to menu item  
        branch: feature/menu-item-schema
        
        @TheTureFADED
        
        """
        with self.DATA_PATH.open("w", encoding="utf-8") as f:
            json.dump(menu_items, f, ensure_ascii=False, indent=2) 
    
