import math
import numpy as np
import pickle
import os
from collections import defaultdict

np.random.seed(0)
class InventoryEnV:
    """
    Giải thích các biến:
    - n_skus: Số lượng sản phẩm
    - lead_time: thời gian giao hàng cố định(số bước)
    - horizon: Số bước thực hiên trong mỗi episode
    - sku_mu: Nhu cầu mua hàng của mỗi sản phẩm
    - sku_sigma:Độ biến động nhu cầu tính theo xấp xỉ Possion
    """
    def __init__(self,n_skus=10000,lead_time=2, horizon=90, sku_mu=None):
        self.n_skus=n_skus
        self.lead_time=lead_time
        self.horizon=90
        if sku_mu is None:
            sku_mu=np.concatenate([np.random.uniform(0,50,size=n_skus//2),np.random.uniform(50,400, size=n_skus-n_skus//2)])
        self.sku_mu=np.array(sku_mu)
        self.sku_sigma=math.sqrt(self.sku_mu)
        self.reset()
    def reset(self):
        #Khởi tạo tồn kho
        self.IP=np.maximum(0,2*self.sku_mu*self.lead_time).astype(int)
        #Khởi tạo đơn hàng đã đặt nhưng chưa về
        self.oo=np.zeros((self.n_skus,self.lead_time),dtype=int)
        #Gắn cờ khuyển mãi cho sản phẩm( các sản phẩm có tỉ lệ 0,5% đễ được gắn cờ khuyến mãi)
        self.promo=(np.random.rand(self.n_skus)<0.05).astype(int)
        #time step
        self.time=0
        return self._get_full_stage()
    def step(self,orders_dict):
        holding_cost=0.01 #Chi phí tồn kho
        stockout_cost= 1 #Chi phí thiếu hàng cho mỗi đơn vị
        orders_fixed_cost= 0.5 # Chi phí cố định cho mỗi lần đặt hàng

        #--------------------1.Đặt hàng------------------------------
        orders=np.zeros(self.n_skus,dtype=int)
        for i, qty in orders_dict.items():
            orders[i]=qty
        self.oo[:,-1]+=orders
        #-------------------2.Khởi tạo nhu cầu cho từng sản phẩm-----
        promo_mul=1.5
        demand_lamda=self.sku_mu*(1+(self.promo*(promo_mul-1)))


        

    