from torch.autograd import Function
import operators.qplacement.ops.lcoupler_legalize.lcoupler_legalize_cpp as lcoupler_legalize_cpp

class LcouplerLegalizeFunction(Function):
    """ Legalize cells with greedy approach 
    """
    @staticmethod
    def forward(
          init_pos,
          pos,
          node_size_x,
          node_size_y,
          node_weights, 
          flat_region_boxes, 
          flat_region_boxes_start, 
          node2fence_region_map, 
          xl, 
          yl, 
          xh, 
          yh, 
          site_width, 
          row_height, 
          num_bins_x, 
          num_bins_y, 
          num_movable_nodes, 
          num_terminal_NIs, 
          num_filler_nodes,
          node_in_group,
          ):
        if pos.is_cuda:
            output = lcoupler_legalize_cpp.forward(
                    init_pos.view(init_pos.numel()).cpu(), 
                    pos.view(pos.numel()).cpu(), 
                    node_size_x.cpu(),
                    node_size_y.cpu(),
                    node_weights.cpu(), 
                    flat_region_boxes.cpu(), 
                    flat_region_boxes_start.cpu(), 
                    node2fence_region_map.cpu(), 
                    xl, 
                    yl, 
                    xh, 
                    yh, 
                    site_width, 
                    row_height, 
                    num_bins_x, 
                    num_bins_y, 
                    num_movable_nodes, 
                    num_terminal_NIs, 
                    num_filler_nodes
                    ).cuda()
        else:
            # print(f'node_size_x ({len(node_size_x)}): {node_size_x.numpy()}')
            # print(f'node_size_y ({len(node_size_y)}): {node_size_y.numpy()}')
            # print(f'xl: {xl}, yl: {yl}, xh: {xh}, yh: {yh}')
            # print(f'site_width: {site_width}, row_height: {row_height}, num_bins_x: {num_bins_x}, num_bins_y: {num_bins_y}')
            assert int(site_width) == 1
            assert int(row_height) == 1
            # print(f'num_movable_nodes: {num_movable_nodes}') 

            # print(f'node_weights: {node_weights.numpy()}')
            # print(f'flat_region_boxes: {flat_region_boxes}')
            # print(f'flat_region_boxes_start: {flat_region_boxes_start}') 
            # print(f'node2fence_region_map: {node2fence_region_map}')
            # print(f'num_terminal_NIs: {num_terminal_NIs}')
            # print(f'num_filler_nodes: {num_filler_nodes}')
            
            output = lcoupler_legalize_cpp.forward(
                    init_pos.view(init_pos.numel()), 
                    pos.view(pos.numel()), 
                    node_size_x,
                    node_size_y,
                    node_weights, 
                    flat_region_boxes, 
                    flat_region_boxes_start, 
                    node2fence_region_map, 
                    xl, 
                    yl, 
                    xh, 
                    yh, 
                    site_width, 
                    row_height, 
                    num_bins_x, 
                    num_bins_y, 
                    num_movable_nodes, 
                    num_terminal_NIs, 
                    num_filler_nodes,
                    node_in_group,
                    )
        return output



class LcouplerLegalize(object):
    """ Legalize cells with greedy approach 
    """
    def __init__(self, node_size_x, node_size_y, node_weights, 
            flat_region_boxes, flat_region_boxes_start, node2fence_region_map, 
            xl, yl, xh, yh, site_width, row_height, num_bins_x, num_bins_y, 
            num_movable_nodes, num_terminal_NIs, num_filler_nodes, node_in_group):
        super(LcouplerLegalize, self).__init__()
        self.node_size_x = node_size_x
        self.node_size_y = node_size_y
        self.node_weights = node_weights
        self.flat_region_boxes = flat_region_boxes 
        self.flat_region_boxes_start = flat_region_boxes_start 
        self.node2fence_region_map = node2fence_region_map
        self.xl = xl 
        self.yl = yl
        self.xh = xh 
        self.yh = yh 
        self.site_width = site_width 
        self.row_height = row_height 
        self.num_bins_x = num_bins_x 
        self.num_bins_y = num_bins_y
        self.num_movable_nodes = num_movable_nodes
        self.num_terminal_NIs = num_terminal_NIs
        self.num_filler_nodes = num_filler_nodes
        self.node_in_group = node_in_group
    def __call__(self, init_pos, pos): 
        """ 
        @param init_pos the reference position for displacement minization
        @param pos current roughly legal position
        """
        return LcouplerLegalizeFunction.forward(
                init_pos, 
                pos,
                node_size_x=self.node_size_x,
                node_size_y=self.node_size_y,
                node_weights=self.node_weights, 
                flat_region_boxes=self.flat_region_boxes, 
                flat_region_boxes_start=self.flat_region_boxes_start, 
                node2fence_region_map=self.node2fence_region_map, 
                xl=self.xl, 
                yl=self.yl, 
                xh=self.xh, 
                yh=self.yh, 
                site_width=self.site_width, 
                row_height=self.row_height, 
                num_bins_x=self.num_bins_x, 
                num_bins_y=self.num_bins_y,
                num_movable_nodes=self.num_movable_nodes, 
                num_terminal_NIs=self.num_terminal_NIs, 
                num_filler_nodes=self.num_filler_nodes,
                node_in_group=self.node_in_group,
                )
