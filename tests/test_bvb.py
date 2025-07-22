from lr1.BVB import BVB
from lr1.JAM import JAM

filename_bvb: str = '/GAMEDATA/RACEC0R1/IGCOLLID.BVB'
filename_jam: str = 'tests/LEGO.JAM'


def test_BVB() -> None:
    bvb: BVB = BVB(JAM(filename_jam).extract_file(filename_bvb))

    test_bvb_materials: str = "['road', 'wood', 'stone', 'walls', 'go_thru', 'shootme']"
    test_bvb_vertices: str = (
        'LRVector3: {X:-583.5477294921875, Y:535.5726318359375, Z:48.80104446411133}'
    )
    test_bvb_polygons: str = 'BVB_Polygon: {v0:0, v1:1, v2:2, Material:3}'
    test_bvb_polygon_ranges: str = 'BVB_PolygonRange: {left:1, right:2, x:679400839, y:831466177, z:460, FirstPoly:0, NumPolys:1}'
    test_bvb_tree: str = 'BVB_PolygonRange: {left:-1, right:-2, x:-564515092, y:913369703, z:0, FirstPoly:315, NumPolys:2}'

    assert str(bvb.materials) == test_bvb_materials
    assert str(bvb.vertices[0]) == test_bvb_vertices
    assert str(bvb.polygons[0]) == test_bvb_polygons
    assert str(bvb.polygon_ranges[0]) == test_bvb_polygon_ranges

    # Check the deepest part of the tree
    assert (
        str(
            bvb.polygon_ranges[
                0
            ].node_left.node_left.node_right.node_left.node_left.node_left.node_left.node_left.node_left.node_left.node_left.node_left.node_left.node_left.node_left.node_left.node_left.node_left.node_left.node_left.node_left.node_left.node_left.node_left.node_right.node_left.node_left.node_left.node_left.node_left.node_right.node_right.node_left.node_left.node_left.node_left.node_left.node_right.node_right.node_left.node_right.node_right.node_left.node_right.node_right.node_right  # type: ignore
        )
        == test_bvb_tree
    )
