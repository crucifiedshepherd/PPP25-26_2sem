import collections.abc
import functools
import itertools
import math
import matplotlib.patches as patches
import matplotlib.pyplot as plt

# вспомогательные чистые мат ф-ии


def get_edges(poly):
    #возвращает итератор пар соседних вершин (ребер)
    return zip(poly, poly[1:] + poly[:1])


def shoelace_area(poly):
    #Вычисление площади многоугольника формулой Гаусса (чистый map/reduce)
    edges = get_edges(poly)
    terms = map(lambda e: e[0][0] * e[1][1] - e[1][0] * e[0][1], edges)
    return abs(functools.reduce(lambda a, b: a + b, terms, 0.0)) / 2.0


def poly_perimeter(poly):
    #Вычисление периметра (чистый map/reduce)
    edges = get_edges(poly)
    dists = map(lambda e: math.hypot(e[0][0] - e[1][0], e[0][1] - e[1][1]), edges)
    return functools.reduce(lambda a, b: a + b, dists, 0.0)

# визуализация

def visualize_polygons(poly_iterator, limit=None, title="Polygons", ax=None, color='none', edgecolor='black'):
    #визуализирует последовательность полигонов из итератора
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_aspect('equal')

    # лениво беру срез бесконечного итератора, если есть лимит
    polys = tuple(itertools.islice(poly_iterator, limit)) if limit else tuple(poly_iterator)

    if not polys:
        return ax

    # создание патчей через map и добавление их на график без циклов for
    patches_list = map(lambda p: patches.Polygon(p, closed=True, facecolor=color, edgecolor=edgecolor, alpha=0.7, linewidth=1.5), polys)
    tuple(map(ax.add_patch, patches_list))

    # автомасштабирование осей через функциональное объединение координат
    all_points = tuple(itertools.chain.from_iterable(polys))
    if all_points:
        xs = tuple(map(lambda p: p[0], all_points))
        ys = tuple(map(lambda p: p[1], all_points))
        ax.set_xlim(min(xs) - 1, max(xs) + 1)
        ax.set_ylim(min(ys) - 1, max(ys) + 1)

    ax.set_title(title)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.axhline(0, color='grey', linewidth=0.5)
    ax.axvline(0, color='grey', linewidth=0.5)
    return ax

# генераторы беск последовательностей

def gen_rectangle(width=2.0, height=1.0, gap=0.5):
    #генерирует беск ленту п/у вдоль оси х
    return map(
        lambda i: (
            (i * (width + gap), 0.0),
            (i * (width + gap), height),
            (i * (width + gap) + width, height),
            (i * (width + gap) + width, 0.0)
        ),
        itertools.count(0)
    )


def gen_triangle(side=2.0, gap=0.5):
    #генерирует беск ленту р/c треугольников на оси x
    h = side * math.sqrt(3) / 2.0
    return map(
        lambda i: (
            (i * (side + gap), 0.0),
            (i * (side + gap) + side / 2.0, h),
            (i * (side + gap) + side, 0.0)
        ),
        itertools.count(0)
    )


def gen_hexagon(radius=1.0, gap=0.5):
    #генерирует беск ленту правильных шестиугольников
    w = math.sqrt(3) * radius
    angles = tuple(map(lambda a: a * math.pi / 3 - math.pi / 6, range(6)))
    return map(
        lambda step: tuple(
            map(lambda a: (step * (w + gap) + radius * math.cos(a), radius + radius * math.sin(a)), angles)
        ),
        itertools.count(0)
    )

# трансформации (через map)

def tr_translate(poly, dx=0.0, dy=0.0):
    #параллельный перенос
    return tuple(map(lambda p: (p[0] + dx, p[1] + dy), poly))


def tr_rotate(poly, angle=0.0, origin=(0.0, 0.0)):
    #поворот вокруг точки origin на angle радиан
    cx, cy = origin
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    return tuple(map(
        lambda p: (
            cx + (p[0] - cx) * cos_a - (p[1] - cy) * sin_a,
            cy + (p[0] - cx) * sin_a + (p[1] - cy) * cos_a
        ), poly
    ))


def tr_homothety(poly, k=1.0, origin=(0.0, 0.0)):
    #масштабирование относительно origin
    cx, cy = origin
    return tuple(map(lambda p: (cx + k * (p[0] - cx), cy + k * (p[1] - cy)), poly))


def tr_symmetry(poly, axis_point=(0.0, 0.0), axis_angle=0.0):
    #осевая симметрия относительно прямой
    p_trans = tr_translate(poly, dx=-axis_point[0], dy=-axis_point[1])
    p_rot = tr_rotate(p_trans, angle=-axis_angle)
    p_sym = tuple(map(lambda p: (p[0], -p[1]), p_rot))
    p_rot_back = tr_rotate(p_sym, angle=axis_angle)
    return tr_translate(p_rot_back, dx=axis_point[0], dy=axis_point[1])

# 5, 7 фильтры и декораторы (доп 1 - все 6 фильтров)

def _apply_filter_decorator(filter_func, **kwargs):
    #создание декораторов фильтрации
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **fn_kwargs):
            new_args = tuple(
                map(
                    lambda arg: filter(functools.partial(filter_func, **kwargs), arg) 
                    if isinstance(arg, collections.abc.Iterator) else arg,
                    args
                )
            )
            return func(*new_args, **fn_kwargs)
        return wrapper
    return decorator


def flt_convex_polygon(poly_or_func=None):
    #выпуклые многоугольники. рработает как предикат и как декоратор
    if callable(poly_or_func):
        return _apply_filter_decorator(flt_convex_polygon)(poly_or_func)
    
    poly = poly_or_func
    n = len(poly)
    if n < 3: 
        return False
    
    triplets = map(lambda i: (poly[i], poly[(i+1)%n], poly[(i+2)%n]), range(n))
    crosses = map(lambda t: (t[1][0] - t[0][0]) * (t[2][1] - t[1][1]) - (t[1][1] - t[0][1]) * (t[2][0] - t[1][0]), triplets)
    
    non_zeros = tuple(filter(lambda c: abs(c) > 1e-9, crosses))
    if not non_zeros: 
        return True
    
    pos = tuple(filter(lambda c: c > 0, non_zeros))
    neg = tuple(filter(lambda c: c < 0, non_zeros))
    return len(pos) == len(non_zeros) or len(neg) == len(non_zeros)


def flt_angle_point(poly=None, target_point=(0.0, 0.0), tol=1e-6):
    #фигуры с углом (вершиной) в заданной точке
    if poly is None:
        return _apply_filter_decorator(flt_angle_point, target_point=target_point, tol=tol)
    return any(map(lambda p: math.hypot(p[0] - target_point[0], p[1] - target_point[1]) < tol, poly))


def flt_square(poly=None, max_area=1.0):
    #фигуры с площадью меньше заданной
    if poly is None:
        return _apply_filter_decorator(flt_square, max_area=max_area)
    return shoelace_area(poly) < max_area


def flt_short_side(poly=None, max_len=1.0):
    #фигуры с кратчайшей стороной меньше заданного значения
    if poly is None:
        return _apply_filter_decorator(flt_short_side, max_len=max_len)
    edges = get_edges(poly)
    min_side = min(map(lambda e: math.hypot(e[0][0] - e[1][0], e[0][1] - e[1][1]), edges))
    return min_side < max_len


def flt_point_inside(poly=None, target_point=(0.0, 0.0)):
    #выпуклые многоугольники, содержащие заданную точку
    if poly is None:
        return _apply_filter_decorator(flt_point_inside, target_point=target_point)
    if not flt_convex_polygon(poly):
        return False
    edges = get_edges(poly)
    signs = tuple(map(lambda e: (e[1][0] - e[0][0]) * (target_point[1] - e[0][1]) - (e[1][1] - e[0][1]) * (target_point[0] - e[0][0]), edges))
    pos = tuple(filter(lambda s: s > 1e-9, signs))
    neg = tuple(filter(lambda s: s < -1e-9, signs))
    return len(pos) == 0 or len(neg) == 0


def flt_polygon_angles_inside(poly=None, target_poly=None):
    #выпуклые многоугольники, содержащие хотя бы один угол заданного полигона
    if poly is None:
        return _apply_filter_decorator(flt_polygon_angles_inside, target_poly=target_poly)
    if not flt_convex_polygon(poly) or target_poly is None:
        return False
    return any(map(lambda pt: flt_point_inside(poly, target_point=pt), target_poly))


# агрегирующие ф-ии (доп. задание 5 - все 5 ф-ий)
# предназначены для использования с functools.reduce

def agr_origin_nearest(poly1, poly2):
    #поиск полигона, самого близкого к началу координат
    dist = lambda poly: min(map(lambda p: math.hypot(p[0], p[1]), poly))
    return poly1 if dist(poly1) <= dist(poly2) else poly2


def agr_max_side(poly1, poly2):
    #поиск полигона с самой длинной стороной
    max_s = lambda poly: max(map(lambda e: math.hypot(e[0][0] - e[1][0], e[0][1] - e[1][1]), get_edges(poly)))
    return poly1 if max_s(poly1) >= max_s(poly2) else poly2


def agr_min_area(poly1, poly2):
    #поиск полигона с самой маленькой площадью
    return poly1 if shoelace_area(poly1) <= shoelace_area(poly2) else poly2


def agr_perimeter(acc, poly):
    #расчет суммарного периметра
    v_acc = acc if isinstance(acc, (float, int)) else poly_perimeter(acc)
    return v_acc + poly_perimeter(poly)


def agr_area(acc, poly):
    #расчет суммарной площади
    v_acc = acc if isinstance(acc, (float, int)) else shoelace_area(acc)
    return v_acc + shoelace_area(poly)

# утилиты склейки и генерации (доп. задание №6 - все 3 утилиты)

def zip_polygons(*iterators):
    #склейка полигонов в одну последовательность (объединение вершин)
    return map(lambda poly_tuple: tuple(itertools.chain.from_iterable(poly_tuple)), zip(*iterators))


def count_2D(start=(0.0, 0.0), step=(1.0, 1.0)):
    #генерация бесконечной 2D последовательности точек
    return map(lambda i: (start[0] + i * step[0], start[1] + i * step[1]), itertools.count(0))


def zip_tuple(*iterables):
    #объединение элементов из итераторов в кортежи
    return map(tuple, zip(*iterables))

# демонстрационный блок (визуализация и тесты)

def run_demonstration():
    print("запуск демонстрации функционального API")

    #рисунок семь фигур всех 3 типов
    fig2, axes2 = plt.subplots(3, 1, figsize=(10, 8))
    visualize_polygons(gen_rectangle(), limit=7, title="Рис 2a: Прямоугольники", ax=axes2[0], edgecolor='blue')
    visualize_polygons(gen_triangle(), limit=7, title="Рис 2б: Треугольники", ax=axes2[1], edgecolor='green')
    visualize_polygons(gen_hexagon(), limit=7, title="Рис 2в: Шестиугольники", ax=axes2[2], edgecolor='purple')
    plt.tight_layout()

    # рисунок трансформации 
    fig3, axes3 = plt.subplots(2, 2, figsize=(12, 12))

    # а) три параллельные ленты под острым углом
    ribbon1 = gen_rectangle(width=1.5, height=0.8, gap=0.2)
    ribbon2 = map(functools.partial(tr_translate, dx=0, dy=1.2), gen_rectangle(1.5, 0.8, 0.2))
    ribbon3 = map(functools.partial(tr_translate, dx=0, dy=2.4), gen_rectangle(1.5, 0.8, 0.2))
    combined_ribbons = itertools.chain.from_iterable(zip(ribbon1, ribbon2, ribbon3))
    tilted_ribbons = map(functools.partial(tr_rotate, angle=math.pi / 6), combined_ribbons)
    visualize_polygons(tilted_ribbons, limit=21, title="Рис 3a: Три ленты под углом", ax=axes3[0, 0])

    # б) две пересекающиеся ленты не в начале координат
    r_base1 = map(functools.partial(tr_translate, dx=-5, dy=3), gen_rectangle(1.5, 0.8, 0.2))
    r_base2 = map(functools.partial(tr_translate, dx=-5, dy=3), gen_rectangle(1.5, 0.8, 0.2))
    r_tilted = map(functools.partial(tr_rotate, angle=math.pi / 3, origin=(-2, 3)), r_base2)
    intersecting_ribbons = itertools.chain.from_iterable(zip(r_base1, r_tilted))
    visualize_polygons(intersecting_ribbons, limit=20, title="Рис 3б: Пересекающиеся ленты", ax=axes3[0, 1])

    # в) две параллельные ленты треугольников, симметричные друг другу
    t_top = map(functools.partial(tr_translate, dx=0, dy=1.0), gen_triangle(side=1.5, gap=0.5))
    t_bottom = map(functools.partial(tr_symmetry, axis_point=(0, 0), axis_angle=0.0), t_top)
    sym_triangles = itertools.chain.from_iterable(zip(t_top, t_bottom))
    visualize_polygons(sym_triangles, limit=14, title="Рис 3в: Симметричные треугольники", ax=axes3[1, 0])

    # г) четырехугольники в разном масштабе
    base_quad = (((1, 0.5), (1, -0.5), (2, -1), (2, 1)),)
    scaled_r = map(lambda k: tr_homothety(base_quad[0], k=k), map(lambda i: 1.0 + i * 0.5, itertools.count(0)))
    scaled_l = map(functools.partial(tr_rotate, angle=math.pi), map(lambda k: tr_homothety(base_quad[0], k=k), map(lambda i: 1.0 + i * 0.5, itertools.count(0))))
    cone_quads = itertools.chain.from_iterable(zip(scaled_r, scaled_l))
    visualize_polygons(cone_quads, limit=10, title="Рис 3г: Масштабируемые четырехугольники", ax=axes3[1, 1])
    plt.tight_layout()

    # рисунок склейка (zip_polygons)
    fig4, ax4 = plt.subplots(figsize=(10, 3))
    t_up = gen_triangle(side=2.0, gap=0.5)
    t_down = map(functools.partial(tr_rotate, angle=math.pi, origin=(1.0, 0.0)), gen_triangle(side=2.0, gap=0.5))
    rhombuses = zip_polygons(t_up, t_down)
    visualize_polygons(rhombuses, limit=6, title="Рис 4: Склейка (zip_polygons -> Ромбы)", ax=ax4, color='orange')
    plt.tight_layout()

    #демонстрация п. 6 и 7 (фильтры и декораторы) ---
    print("\nДемонстрация применения фильтров (Пункт 6.1)")
    
    # применяем декоратор @flt_square (оставит фигуры с площадью < 2.0)
    @flt_square(max_area=2.0)
    def process_polygons(iterator):
        # берем ровно 6 фигур (требование 6.1)
        return itertools.islice(iterator, 6)

    # генерируем ленту четырехугольников из п.4б (их площадь 1.5 * 0.8 = 1.2, фильтр их пропустит)
    it_4b = itertools.chain.from_iterable(
        zip(
            map(functools.partial(tr_translate, dx=-5, dy=3), gen_rectangle(1.5, 0.8, 0.2)),
            map(functools.partial(tr_rotate, angle=math.pi/3, origin=(-2,3)), map(functools.partial(tr_translate, dx=-5, dy=3), gen_rectangle(1.5, 0.8, 0.2)))
        )
    )
    res_6_polys = tuple(process_polygons(it_4b))
    print(f"Отфильтровано и получено ровно фигур: {len(res_6_polys)}")

    #демонстрация п. 8 (все 5 агрегирующих функций через reduce)
    print("\nДемонстрация агрегирующих функций reduce (Доп. задание №5)")
    test_polys = tuple(itertools.islice(gen_rectangle(width=3, height=4, gap=1), 5))
    # 5 прямоугольников 3x4
    
    print("Ближайший к началу координат:", functools.reduce(agr_origin_nearest, test_polys))
    print("С максимальной стороной (длина 4):", functools.reduce(agr_max_side, test_polys))
    print("С минимальной площадью (все равны 12):", functools.reduce(agr_min_area, test_polys))
    print("Суммарный периметр (5 фигур * 14):", functools.reduce(agr_perimeter, test_polys, 0.0))
    print("Суммарная площадь (5 фигур * 12):", functools.reduce(agr_area, test_polys, 0.0))

    plt.show()


if __name__ == "__main__":
    run_demonstration()