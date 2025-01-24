from stellar_sdk import Asset
from services.logging_service import logging_service

ETF_ASSETLIST = [
    {"asset_code": "XLM", "issuer": "native", "enabled": True, "allocation": 0.2},
    {"asset_code": "USDC", "issuer": "GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN", "enabled": True, "allocation": 0.2},
    {"asset_code": "EURC", "issuer": "GDHU6WRG4IEQXM5NZ4BMPKOXHW76MZM4Y2IEMFDVXBSDP6SJY4ITNPP2", "enabled": True, "allocation": 0.1},
    {"asset_code": "ARS", "issuer": "GCYE7C77EB5AWAA25R5XMWNI2EDOKTTFTTPZKM2SR5DI4B4WFD52DARS", "enabled": True, "allocation": 0.025},
    {"asset_code": "AFR", "issuer": "GBX6YI45VU7WNAAKA3RBFDR3I3UKNFHTJPQ5F6KOOKSGYIAM4TRQN54W", "enabled": True, "allocation": 0.025},    
    {"asset_code": "BTC", "issuer": "GDPJALI4AZKUU2W426U5WKMAT6CN3AJRPIIRYR2YM54TL2GDWO5O2MZM", "enabled": True, "allocation": 0.1},
    {"asset_code": "ETH", "issuer": "GBFXOHVAS43OIWNIO7XLRJAHT3BICFEIKOJLZVXNT572MISM4CMGSOCC", "enabled": True, "allocation": 0.05},
    {"asset_code": "AQUA", "issuer": "GBNZILSTVQZ4R7IKQDGHYGY2QXL5QOFJYQMXPKWRRM5PAV7Y4M67AQUA", "enabled":True, "allocation": 0.05},    
    {"asset_code": "VELO", "issuer": "GDM4RQUQQUVSKQA7S6EM7XBZP3FCGH4Q7CL6TABQ7B2BEJ5ERARM2M5M", "enabled": True, "allocation": 0.05},
    {"asset_code": "SHX", "issuer": "GDSTRSHXHGJ7ZIVRBXEYE5Q74XUVCUSEKEBR7UCHEUUEK72N7I7KJ6JH", "enabled": True, "allocation": 0.05},
    {"asset_code": "XRP", "issuer": "GBXRPL45NPHCVMFFAYZVUVFFVKSIZ362ZXFP7I2ETNQ3QKZMFLPRDTD5", "enabled": True, "allocation": 0.05},
    {"asset_code": "FRED", "issuer": "GCA73U2PZFWAXJSNVMEVPNPPJCZGETWPWZC6E4DJAIWP3ZW3BAGYZLV6", "enabled": True, "allocation": 0.02},
    {"asset_code": "SOLS", "issuer": "GAWTJMZIR4KPCZ7BQZK6QRAJYT6FOIM3YP2MKGWOYHPJYQQOIEJWFRED", "enabled": True, "allocation": 0.02},
    {"asset_code": "UBEC", "issuer": "GDPNB7S3IOM2J6C3NA2QG4TQAUCRZXPJJ4HSCSIKELEH7ORUCX5UB2VN", "enabled": True, "allocation": 0.02},
    {"asset_code": "SCOP", "issuer": "GC6OYQJIZF3HFXCYPFCBXYXNGIBQ4TNSFUBUXQJOZWIP6F3YZK4QH3VQ", "enabled": True, "allocation": 0.02},
    {"asset_code": "SSLX", "issuer": "GBHFGY3ZNEJWLNO4LBUKLYOCEK4V7ENEBJGPRHHX7JU47GWHBREH37UR", "enabled": True, "allocation": 0.02}, 
    {"asset_code": "TFT", "issuer": "GBOVQKJYHXRR3DX6NOX2RRYFRCUMSADGDESTDNBDS6CDVLGVESRTAC47", "enabled": False, "allocation": 0.0},
    {"asset_code": "asSOL", "issuer": "GALLBRBQHAPW5FOVXXHYWR6J4ZDAQ35BMSNADYGBW25VOUHUYRZM4XIL", "enabled": False, "allocation": 0.0},
    {"asset_code": "NUNA", "issuer": "GCX2ENOVSSOOH6G4HIOBMPCBFXHDVDGA546NK3ZFX3NP3QS25BKZBWOW", "enabled": False, "allocation": 0.0}, 
    {"asset_code": "ETFToken", "issuer": "GAM4XF53LDYEDMFQO7VGZHK4H4RJEMOSHTKSQEC6KHHNB5JXU5T4VETF", "enabled": False, "allocation": 0.0},                      
# Add more trade listed assets here
]

class DynamicAssetManager:
    def __init__(self):
        self.etf_assetlist = ETF_ASSETLIST
        self.logger = logging_service
        self.logger.info("Dynamic Asset Manager initialized")

    def enable_asset(self, asset_code):
        """Enable an asset by its code."""
        for asset in self.etf_assetlist:
            if asset["asset_code"] == asset_code:
                asset["enabled"] = True
                self.logger.info(f"Asset {asset_code} has been enabled.")
                return
        self.logger.warning(f"Asset {asset_code} not found in the trade asset list.")

    def disable_asset(self, asset_code):
        """Disable an asset by its code."""
        for asset in self.etf_assetlist:
            if asset["asset_code"] == asset_code:
                asset["enabled"] = False
                self.logger.info(f"Asset {asset_code} has been disabled.")
                return
        self.logger.warning(f"Asset {asset_code} not found in the trade asset list.")

    def get_enabled_assets(self):
        """Retrieve the list of currently enabled assets."""
        enabled_assets = [asset for asset in self.etf_assetlist if asset["enabled"]]
        self.logger.debug(f"Enabled assets: {[asset['asset_code'] for asset in enabled_assets]}")
        return enabled_assets

    def update_asset_status(self, asset_code, status):
        """Update the enabled status of an asset dynamically."""
        for asset in self.etf_assetlist:
            if asset["asset_code"] == asset_code:
                asset["enabled"] = status
                action = "enabled" if status else "disabled"
                self.logger.info(f"Asset {asset_code} has been {action}.")
                return
        self.logger.warning(f"Asset {asset_code} not found in the trade asset list.")

    def get_asset_allocation(self, asset_code):
        """Retrieve allocation for a specific asset."""
        for asset in self.etf_assetlist:
            if asset["asset_code"] == asset_code:
                return asset["allocation"]
        return 0.0

# Singleton instance for easy access
dynamic_asset_manager = DynamicAssetManager()

