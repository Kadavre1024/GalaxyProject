
def transform(self, x, y):
    #return self.transform_2D(x, y)
    return self.transform_perspective(x, y)

def transform_2D(self, x, y):
    return int(x), int(y)

def transform_perspective(self ,pt_x ,pt_y):
    lin_y = pt_y *self.perspective_point_y /self.height
    diff_x = pt_x - self.perspective_point_x
    factor_y = (self.perspective_point_y - lin_y ) /self.perspective_point_y
    factor_y = pow(factor_y, 4)

    tr_x = self.perspective_point_x + diff_x *factor_y
    tr_y = self.perspective_point_y - factor_y *self.perspective_point_y
    return int(tr_x), int(tr_y)