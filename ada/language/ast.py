from __future__ import absolute_import

from langkit import compiled_types
from langkit.compiled_types import (
    ASTNode, BoolType, EnumType, Field, Struct, UserField, abstract,
    env_metadata, root_grammar_class, LongType, create_macro
)

from langkit.envs import EnvSpec
from langkit.expressions import (
    AbstractProperty, And, Env, Let, Not, is_simple_expr
)
from langkit.expressions import New
from langkit.expressions import Property
from langkit.expressions import Self
from langkit.expressions.boolean import If


@env_metadata
class Metadata(Struct):
    dottable_subprogram = UserField(
        BoolType, doc="Whether the stored element is a subprogram accessed "
                      "through the dot notation"
    )
    implicit_deref = UserField(
        BoolType, doc="Whether the stored element is accessed through an "
                      "implicit dereference"
    )


@abstract
@root_grammar_class
class AdaNode(ASTNode):
    """
    Root node class for the Ada grammar. This is good and necessary for several
    reasons:

    1. It will facilitate the sharing of langkit_support code if we ever have
       two libraries generated by LanguageKit in the same application.

    2. It allows to insert code specific to the ada root node, without
       polluting every LanguageKit node, and without bringing back the root
       ASTNode in the code templates.
    """
    pass


def child_unit(name_expr, env_val_expr=Self):
    """
    This macro will add the properties and the env specification necessary
    to make a node implement the specification of a library child unit in
    Ada, so that you can declare new childs to an unit outside of its own
    scope.

    :param AbstractExpression env_val_expr: The expression that will
        retrieve the environment value for the decorated node.

    :param AbstractExpression name_expr: The expression that will retrieve
        the name value for the decorated node.

    :rtype: NodeMacro
    """

    attribs = dict(
        scope=Property(name_expr.scope, private=True, doc="""
                       Helper property, that will return the scope of
                       definition of this child unit.
                       """),
        env_spec=EnvSpec(
            initial_env=Self.scope, add_env=True, add_to_env=(
                (name_expr, env_val_expr) if is_simple_expr(name_expr)
                else (Self.env_spec_name, env_val_expr)
            )
        )
    )
    # Add a property if the name expr is not a simple expr
    if is_simple_expr(name_expr):
        attribs['env_spec_name'] = Property(name_expr, private=True),

    return create_macro(attribs)


class DiscriminantSpec(AdaNode):
    ids = Field()
    type_expr = Field()
    default_expr = Field()


class TypeDiscriminant(AdaNode):
    discr_specs = Field()


@abstract
class TypeDef(AdaNode):
    pass


class EnumTypeDef(TypeDef):
    enum_literals = Field()


class Variant(AdaNode):
    choice_list = Field()
    components = Field()


class VariantPart(AdaNode):
    discr_name = Field()
    variant = Field()


class ComponentDecl(AdaNode):
    ids = Field()
    component_def = Field()
    default_expr = Field()
    aspects = Field()


class ComponentList(AdaNode):
    components = Field()
    variant_part = Field()


class RecordDef(AdaNode):
    components = Field()
    env_spec = EnvSpec(add_env=True)


class RecordTypeDef(TypeDef):
    abstract = Field()
    tagged = Field()
    limited = Field()
    record_def = Field()


@abstract
class RealTypeDef(TypeDef):
    pass


class FullTypeDecl(AdaNode):
    type_id = Field()
    discriminants = Field()
    type_def = Field()
    aspects = Field()

    name = Property(Self.type_id)
    env_spec = EnvSpec(add_to_env=(Self.name, Self))


class FloatingPointDef(RealTypeDef):
    num_digits = Field()
    range = Field()


class OrdinaryFixedPointDef(RealTypeDef):
    delta = Field()
    range = Field()


class DecimalFixedPointDef(RealTypeDef):
    delta = Field()
    digits = Field()
    range = Field()


@abstract
class Constraint(AdaNode):
    pass


class RangeConstraint(Constraint):
    range = Field()


class DigitsConstraint(Constraint):
    digits = Field()
    range = Field()


class DeltaConstraint(Constraint):
    digits = Field()
    range = Field()


class IndexConstraint(Constraint):
    constraints = Field()


class DiscriminantConstraint(Constraint):
    constraints = Field()


class DiscriminantAssociation(Constraint):
    ids = Field()
    expr = Field()


class DerivedTypeDef(TypeDef):
    abstract = Field()
    limited = Field()
    synchronized = Field()
    null_exclusion = Field()
    name = Field()
    constraint = Field()
    interfaces = Field()
    record_extension = Field()
    has_private_part = Field()


class IncompleteTypeDef(TypeDef):
    is_tagged = Field()


class PrivateTypeDef(TypeDef):
    abstract = Field()
    tagged = Field()
    limited = Field()


class SignedIntTypeDef(TypeDef):
    range = Field()


class ModIntTypeDef(TypeDef):
    expr = Field()


@abstract
class ArrayIndices(AdaNode):
    pass


class UnconstrainedArrayIndices(ArrayIndices):
    list = Field()


class ConstrainedArrayIndices(ArrayIndices):
    list = Field()


class ComponentDef(AdaNode):
    aliased = Field()
    type_expr = Field()


class ArrayTypeDef(TypeDef):
    indices = Field()
    stored_component = Field()


class InterfaceKind(EnumType):
    alternatives = ["limited", "task", "protected", "synchronized"]
    suffix = 'interface'


class InterfaceTypeDef(TypeDef):
    interface_kind = Field()
    interfaces = Field()


class SubtypeDecl(AdaNode):
    # Fields
    id = Field()
    type_expr = Field()
    aspects = Field()

    # Properties
    name = Property(Self.id, doc='Name for the declared subtype')

    env_spec = EnvSpec(add_to_env=(Self.name, Self))


class TaskDef(AdaNode):
    items = Field()
    private_items = Field()
    end_id = Field()


class ProtectedDef(AdaNode):
    public_ops = Field()
    private_components = Field()
    end_id = Field()


class TaskTypeDecl(AdaNode):
    task_type_name = Field()
    discrs = Field()
    aspects = Field()
    interfaces = Field()
    definition = Field()


class ProtectedTypeDecl(AdaNode):
    task_type_name = Field()
    discrs = Field()
    aspects = Field()
    interfaces = Field()
    definition = Field()


class AccessDef(TypeDef):
    not_null = Field()
    access_expr = Field()


class FormalDiscreteTypeDef(TypeDef):
    pass


class NullComponentDecl(AdaNode):
    pass


class WithDecl(AdaNode):
    is_limited = Field()
    is_private = Field()
    packages = Field()


@abstract
class UseDecl(AdaNode):
    pass


class UsePkgDecl(UseDecl):
    packages = Field()


class UseTypDecl(UseDecl):
    all = Field()
    types = Field()


class TypeExpression(AdaNode):
    """
    This type will be used as a base for what represents a type expression
    in the Ada syntax tree.
    """
    null_exclusion = Field()
    type_expr_variant = Field()


@abstract
class TypeExprVariant(AdaNode):
    pass


class TypeRef(TypeExprVariant):
    name = Field()
    constraint = Field()


@abstract
class AccessExpression(TypeExprVariant):
    pass


class SubprogramAccessExpression(AccessExpression):
    is_protected = Field(repr=False)
    subp_spec = Field()


class TypeAccessExpression(AccessExpression):
    is_all = Field()
    is_constant = Field()
    subtype_name = Field()


class ParameterProfile(AdaNode):
    ids = Field()
    is_aliased = Field(repr=False)
    mode = Field()
    type_expr = Field()
    default = Field()


class AspectSpecification(AdaNode):
    aspect_assocs = Field()


class SubprogramDecl(AdaNode):
    _macros = [child_unit(Self.name, Self.subp_spec)]

    is_overriding = Field()
    subp_spec = Field()
    is_null = Field()
    is_abstract = Field()
    expression = Field()
    renames = Field()
    aspects = Field(repr=False)

    name = Property(Self.subp_spec.name)


class Pragma(AdaNode):
    id = Field()
    args = Field()


class PragmaArgument(AdaNode):
    id = Field()
    expr = Field()


######################
# GRAMMAR DEFINITION #
######################

class InOut(EnumType):
    alternatives = ["in", "out", "inout"]
    suffix = 'way'


@abstract
class AspectClause(AdaNode):
    pass


class EnumRepClause(AspectClause):
    type_name = Field()
    aggregate = Field()


class AttributeDefClause(AspectClause):
    attribute_expr = Field()
    expr = Field()


class RecordRepComponent(AdaNode):
    id = Field()
    position = Field()
    range = Field()


class RecordRepClause(AspectClause):
    component_name = Field()
    at_expr = Field()
    components = Field()


class AtClause(AspectClause):
    name = Field()
    expr = Field()


class EntryDecl(AdaNode):
    overriding = Field()
    entry_id = Field()
    family_type = Field()
    params = Field()
    aspects = Field()


class TaskDecl(AdaNode):
    task_name = Field()
    aspects = Field()
    definition = Field()


class ProtectedDecl(AdaNode):
    protected_name = Field()
    aspects = Field()
    definition = Field()


class AspectAssoc(AdaNode):
    id = Field()
    expr = Field()


class NumberDecl(AdaNode):
    ids = Field()
    expr = Field()


class ObjectDecl(AdaNode):
    ids = Field()
    aliased = Field()
    constant = Field()
    inout = Field()
    type = Field()
    default_expr = Field()
    renaming_clause = Field()
    aspects = Field()

    env_spec = EnvSpec(add_to_env=(Self.ids, Self))


class PrivatePart(AdaNode):
    decls = Field()
    env_spec = EnvSpec(add_env=True)


class BasePackageDecl(AdaNode):
    """
    Package declarations. Concrete instances of this class
    will be created in generic package declarations. Other non-generic
    package declarations will be instances of PackageDecl.

    The behavior is the same, the only difference is that BasePackageDecl
    and PackageDecl have different behavior regarding lexical environments.
    In the case of generic package declarations, we use BasePackageDecl
    which has no env_spec, and the environment behavior is handled by the
    GenericPackageDecl instance.
    """
    package_name = Field()
    aspects = Field()
    decls = Field()
    private_part = Field()
    end_id = Field()

    name = Property(Self.package_name, private=True)


class PackageDecl(BasePackageDecl):
    """
    Non-generic package declarations.
    """
    _macros = [child_unit(Self.name)]


class ExceptionDecl(AdaNode):
    """
    Exception declarations.
    """
    ids = Field()
    renames = Field()
    aspects = Field()


class GenericInstantiation(AdaNode):
    """
    Instantiations of generics.
    """
    name = Field()
    generic_entity_name = Field()
    parameters = Field()
    aspects = Field()


class RenamingClause(AdaNode):
    """
    Renaming clause, used everywhere renamings are valid.
    """
    renamed_object = Field()


class PackageRenamingDecl(AdaNode):
    name = Field()
    renames = Field(type=RenamingClause)
    aspects = Field()


class GenericRenamingDecl(AdaNode):
    name = Field()
    renames = Field()
    aspects = Field()


class FormalSubpDecl(AdaNode):
    """
    Formal subprogram declarations, in generic declarations formal parts.
    """
    subp_spec = Field()
    is_abstract = Field()
    default_value = Field()


class Overriding(EnumType):
    alternatives = ["overriding", "not_overriding", "unspecified"]
    suffix = 'kind'


class GenericSubprogramDecl(AdaNode):
    formal_part = Field()
    subp_spec = Field()
    aspects = Field()


class GenericPackageDecl(AdaNode):
    _macros = [child_unit(Self.name)]

    formal_part = Field()
    package_decl = Field(type=BasePackageDecl)
    name = Property(Self.package_decl.name)


def is_package(e):
    """
    Property helper to determine if an entity is a package or not.

    TODO: This current solution is not really viable, because:
    1. Having to do local imports of AdaNode subclasses is tedious.
    2. is_package could be useful in other files.

    This probably hints towards a reorganization of the types definition.

    :type e: AbstractExpression
    :rtype: AbstractExpression
    """
    return e.is_a(PackageDecl, PackageBody)


@abstract
class Expr(AdaNode):
    designated_env = AbstractProperty(
        type=compiled_types.LexicalEnvType, private=True, runtime_check=True,
        doc="""
        Returns the lexical environment designated by this name.
        """
    )

    scope = AbstractProperty(
        type=compiled_types.LexicalEnvType, private=True, runtime_check=True,
        doc="""
        Returns the lexical environment that is the scope in which the
        entity designated by this name is defined/used.
        """
    )

    name = AbstractProperty(
        type=compiled_types.Token, private=True, runtime_check=True,
        doc="""
        Returns the relative name of this instance. For example,
        for a prefix A.B.C, this will return C.
        """
    )

    env_elements = AbstractProperty(
        type=compiled_types.EnvElement.array_type(), runtime_check=True,
        doc="""
        Returns the list of annotated elements in the lexical environment
        that can statically be a match for expr before overloading analysis.
        """
    )

    entities = Property(
        Self.env_elements.map(lambda e: e.el), type=AdaNode.array_type(),
        doc="""
        Same as env_elements, but return bare AdaNode instances rather than
        EnvElement instances.
        """
    )

    get_type = AbstractProperty(
        type=AdaNode, runtime_check=True,
        doc="""
        Get the type pointed at by expr. Since in ada this can be resolved
        locally without any non-local analysis, this doesn't use logic
        equations.
        """
    )


class UnOp(Expr):
    op = Field()
    expr = Field()


class BinOp(Expr):
    left = Field()
    op = Field()
    right = Field()


class MembershipExpr(Expr):
    expr = Field()
    op = Field()
    membership_exprs = Field()


class Aggregate(Expr):
    ancestor_expr = Field()
    assocs = Field()


class CallExpr(Expr):
    name = Field()
    paren_tok = Field(repr=False)
    suffix = Field()


class ParamAssoc(AdaNode):
    designator = Field()
    expr = Field()


class ParamList(AdaNode):
    params = Field()


class AccessDeref(Expr):
    pass


class DiamondExpr(Expr):
    pass


class OthersDesignator(AdaNode):
    pass


class AggregateMember(AdaNode):
    choice_list = Field()


class Op(EnumType):
    """Operation in a binary expression."""
    alternatives = ["and", "or", "or_else", "and_then", "xor", "in",
                    "not_in", "abs", "not", "pow", "mult", "div", "mod",
                    "rem", "plus", "minus", "bin_and", "eq", "neq", "lt",
                    "lte", "gt", "gte", "ellipsis"]
    suffix = 'op'


class IfExpr(Expr):
    cond_expr = Field()
    then_expr = Field()
    elsif_list = Field()
    else_expr = Field()


class ElsifExprPart(AdaNode):
    cond_expr = Field()
    then_expr = Field()


class CaseExpr(Expr):
    expr = Field()
    cases = Field()


class CaseExprAlternative(Expr):
    choices = Field()
    expr = Field()


@abstract
class SingleTokNode(Expr):
    tok = Field()
    name = Property(Self.tok, private=True)
    sym = Property(Self.tok.symbol, private=True)

    matches = Property(
        type=BoolType,
        doc="""
        Return whether this token and the "other" one are the same.

        This is only defined for two nodes that wrap symbols.
        """,
        expr=lambda other=(lambda: SingleTokNode):
            Self.name.symbol.equals(other.name.symbol)
    )


class BaseId(SingleTokNode):
    designated_env = Property(
        Env.resolve_unique(Self.tok).el.parent_env, private=True
    )
    scope = Property(Env, private=True)
    name = Property(Self.tok, private=True)

    # This implementation of get_type is more permissive than the "legal" one
    # since it will skip entities that are eventually available first in the
    # env, shadowing the actual type, if they are not types. It will allow
    # to get working XRefs in simple shadowing cases.
    get_type = Property(
        Self.entities.filter(lambda e: e.is_a(SubtypeDecl, FullTypeDecl)).at(0)
    )

    has_callexpr = Property(
        Not(Self.parents.take_while(lambda p: (
            p.is_a(CallExpr)
            | p.parent.is_a(CallExpr)
            | p.parent.cast(Prefix).then(lambda pfx: pfx.suffix.equals(p))
        )).empty),
        type=BoolType,
        doc="""
        This property will return whether this BaseId is the main symbol
        qualifying the entity in a Call expression. For example::

            C (12, 15);
            ^ has_callexpr = True

            A.B.C (12, 15);
                ^ has_callexpr = True

            A.B.C (12, 15);
              ^ has_callexpr = False
        """
    )

    env_elements = Property(
        If(Self.has_callexpr,
           # If self id is the main id in a callexpr, we'll let the
           # filtering to the callexpr. Callexpr.env_elements will call this
           # implementation and do its own filtering.
           Env.get(Self.tok),

           # If it is not the main id in a callexpr, then we want to filter
           # the components that would only be valid with a callexpr.
           Env.get(Self.tok).filter(
               lambda e: e.el.cast(SubprogramSpec).then(lambda ss: (
                   (e.MD.dottable_subprogram & ss.nb_min_params.equals(1))
                   | ss.nb_min_params.equals(0)
               ), default_val=True)
           ))
    )


class Identifier(BaseId):
    _repr_name = "Id"


class StringLiteral(BaseId):
    _repr_name = "Str"


class EnumIdentifier(Identifier):
    _repr_name = "EnumId"


class CharLiteral(SingleTokNode):
    _repr_name = "Chr"


class NumLiteral(SingleTokNode):
    _repr_name = "Num"


class NullLiteral(SingleTokNode):
    _repr_name = "Null"


class Attribute(SingleTokNode):
    _repr_name = "Attr"


class SingleParameter(Struct):
    name = Field(type=Identifier)
    profile = Field(type=ParameterProfile)


class ParamMatch(Struct):
    """
    Helper data structure to implement SubprogramSpec/ParamAssocList matching.

    Each value relates to one ParamAssoc.
    """
    has_matched = Field(type=BoolType, doc="""
        Whether the matched ParamAssoc a ParameterProfile.
    """)
    is_formal_opt = Field(type=BoolType, doc="""
        Whether the matched ParameterProfile has a default value (and is thus
        optional).
    """)


class SubprogramSpec(AdaNode):
    name = Field()
    params = Field()
    returns = Field()

    typed_param_list = Property(
        Self.params.mapcat(
            lambda profile: profile.ids.map(lambda id: (
                New(SingleParameter, name=id, profile=profile)
            ))
        ),
        doc='Collection of couples (identifier, param profile) for all'
            ' parameters'
    )

    nb_min_params = Property(
        Self.typed_param_list.filter(
            lambda p: p.profile.default.is_null,
        ).length,
        type=LongType, doc="""
        Return the minimum number of parameters this subprogram can be called
        while still being a legal call.
        """
    )

    nb_max_params = Property(
        Self.typed_param_list.length, type=LongType,
        doc="""
        Return the maximum number of parameters this subprogram can be called
        while still being a legal call.
        """
    )

    match_param_list = Property(
        type=ParamMatch.array_type(),
        doc="""
        For each ParamAssoc in a ParamList, return whether we could find a
        matching formal in this SubprogramSpec and whether this formal is
        optional (i.e. has a default value).
        """,
        expr=lambda params=ParamList: Let(
            lambda
            typed_params=Self.typed_param_list,
            no_match=New(ParamMatch,
                         has_matched=False,
                         is_formal_opt=False):

            params.params.map(lambda i, pa: If(
                pa.designator.is_null,

                # Positional parameter case: if this parameter has no
                # name association, make sure we have enough formals.
                typed_params.at(i).then(lambda single_param: New(
                    ParamMatch,
                    has_matched=True,
                    is_formal_opt=Not(single_param.profile.default.is_null)
                ), no_match),

                # Named parameter case: make sure the designator is
                # actualy a name and that there is a corresponding
                # formal.
                pa.designator.cast(Identifier).then(lambda id: (
                    typed_params.find(lambda p: p.name.matches(id)).then(
                        lambda p: New(
                            ParamMatch,
                            has_matched=True,
                            is_formal_opt=Not(p.profile.default.is_null)
                        ), no_match
                    )
                ), no_match)
            ))
        )
    )

    is_matching_param_list = Property(
        type=BoolType,
        doc="""
        Return whether a ParamList is a match for this SubprogramSpec, i.e.
        whether the argument count (and designators, if any) match.
        """,
        expr=lambda params=ParamList: Let(
            lambda match_list=Self.match_param_list(params): And(
                match_list.all(lambda m: m.has_matched),
                match_list.filter(
                    lambda m: Not(m.is_formal_opt)
                ).length.equals(Self.nb_min_params),
                params.params.length <= Self.nb_max_params
            )
        )
    )

    match_param_assoc = Property(
        type=BoolType,
        doc="""
        Return whether some parameter association matches an argument in this
        subprogram specification. Note that this matching disregards types: it
        only considers arity and designators (named parameters).
        """,
        expr=lambda pa=ParamAssoc: (
            # Parameter associations can match only if there is at least one
            # formal in this spec.
            (Self.nb_max_params > 0)

            & (
                # Then, all associations with no designator match, as we don't
                # consider types.
                Not(pa.designator.is_null)

                # The ones with a designator match iff the designator is an
                # identifier whose name is present in the list of formals.
                | pa.designator.cast(Identifier).then(
                    lambda id: Self.typed_param_list.any(
                        lambda p: p.name.matches(id)
                    )
                )
            )
        )
    )


class Quantifier(EnumType):
    alternatives = ["all", "some"]
    suffix = 'items'


class IterType(EnumType):
    alternatives = ["in", "of"]
    suffix = 'iter'


@abstract
class LoopSpec(AdaNode):
    pass


class ForLoopSpec(LoopSpec):
    id = Field()
    loop_type = Field()
    is_reverse = Field()
    iter_expr = Field()


class QuantifiedExpr(Expr):
    quantifier = Field()
    loop_spec = Field()
    expr = Field()


class Allocator(Expr):
    subpool = Field()
    expr = Field()


class QualExpr(Expr):
    prefix = Field()
    suffix = Field()


@abstract
class AbstractAggregateContent(AdaNode):
    pass


class AggregateContent(AbstractAggregateContent):
    fields = Field()


class AggregateAssoc(AdaNode):
    designator = Field()
    expr = Field()


class AttributeRef(Expr):
    prefix = Field()
    attribute = Field()
    args = Field()


class RaiseExpression(Expr):
    exception_name = Field()
    error_message = Field()


class Prefix(Expr):
    prefix = Field()
    suffix = Field()

    designated_env = Property(
        Self.prefix.designated_env.eval_in_env(Self.suffix.designated_env),
        private=True
    )

    scope = Property(Self.prefix.designated_env, private=True)

    name = Property(Self.suffix.name, private=True)

    env_elements = Property(
        Self.prefix.designated_env.eval_in_env(Self.suffix.env_elements)
    )

    # This implementation of get_type is more permissive than the "legal" one
    # since it will skip entities that are eventually available first in the
    # env if they are not packages.
    get_type = Property(lambda self: (
        self.prefix.entities.filter(is_package).at(0).parent_env.eval_in_env(
            self.suffix.get_type
        )
    ))


class CompilationUnit(AdaNode):
    """Root node for all Ada analysis units."""
    prelude = Field(doc="``with``, ``use`` or ``pragma`` statements.")
    bodies = Field()

    env_spec = EnvSpec(add_env=True)


class SubprogramBody(AdaNode):
    _macros = [child_unit(Self.name, Self.subp_spec)]

    overriding = Field()
    subp_spec = Field()
    aspects = Field()
    decls = Field()
    statements = Field()
    end_id = Field()

    name = Property(Self.subp_spec.name)


class HandledStatements(AdaNode):
    statements = Field()
    exceptions = Field()


class ExceptionHandler(AdaNode):
    exc_name = Field()
    catched_exceptions = Field()
    statements = Field()


@abstract
class Statement(AdaNode):
    pass


class NullStatement(Statement):
    null_lit = Field(repr=False)


class AssignStatement(Statement):
    dest = Field()
    expr = Field()


class GotoStatement(Statement):
    label_name = Field()


class ExitStatement(Statement):
    loop_name = Field()
    condition = Field()


class ReturnStatement(Statement):
    return_expr = Field()


class RequeueStatement(Statement):
    call_name = Field()
    with_abort = Field()


class AbortStatement(Statement):
    names = Field()


class DelayStatement(Statement):
    until = Field()
    expr = Field()


class RaiseStatement(Statement):
    exception_name = Field()
    error_message = Field()


class IfStatement(Statement):
    condition = Field()
    statements = Field()
    alternatives = Field()
    else_statements = Field()


class ElsifStatementPart(AdaNode):
    expr = Field()
    statements = Field()


class Label(Statement):
    token = Field()


class WhileLoopSpec(LoopSpec):
    expr = Field()


class LoopStatement(Statement):
    name = Field()
    spec = Field()
    statements = Field()


class BlockStatement(Statement):
    name = Field()
    decls = Field()
    statements = Field()

    env_spec = EnvSpec(add_env=True)


class ExtReturnStatement(AdaNode):
    object_decl = Field()
    statements = Field()


class CaseStatement(Statement):
    case_expr = Field()
    case_alts = Field()


class CaseStatementAlternative(AdaNode):
    choices = Field()
    statements = Field()


class AcceptStatement(Statement):
    name = Field()
    entry_index_expr = Field()
    parameters = Field()
    statements = Field()


class SelectStatement(Statement):
    guards = Field()
    else_statements = Field()
    abort_statements = Field()


class SelectWhenPart(Statement):
    choices = Field()
    statements = Field()


class TerminateStatement(Statement):
    pass


class PackageBody(AdaNode):
    _macros = [child_unit(Self.name)]

    package_name = Field()
    aspects = Field()
    decls = Field()
    statements = Field()

    name = Property(Self.package_name, private=True)


class TaskBody(AdaNode):
    package_name = Field()
    aspects = Field()
    decls = Field()
    statements = Field()


class ProtectedBody(AdaNode):
    package_name = Field()
    aspects = Field()
    decls = Field()
    body_stub = Field()


class EntryBody(AdaNode):
    entry_name = Field()
    index_spec = Field()
    parameters = Field()
    when_cond = Field()
    decls = Field()
    statements = Field()


class EntryIndexSpec(AdaNode):
    id = Field()
    subtype = Field()


class Subunit(AdaNode):
    name = Field()
    body = Field()


class BodyStub(AdaNode):
    aspects = Field()


class SubprogramBodyStub(AdaNode):
    overriding = Field()
    subp_spec = Field()
    aspects = Field()


class PackageBodyStub(AdaNode):
    name = Field()
    aspects = Field()


class LibraryItem(AdaNode):
    is_private = Field()
    item = Field()
