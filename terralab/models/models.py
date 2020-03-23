# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

logger = logging.getLogger(__name__)

# Terralab models

class SampleType(models.Model):
    _name = 'terralab.sampletype'
    _description = 'TerraLab Sample Type'
    samples = fields.One2many('terralab.sample', 'sample_type', 'Samples') # There are many Samples of one SampleType
    test_types = fields.One2many('product.template', 'terralab_sample_type', 'Test Types') # There are many TestTypes of one SampleType (they are Products)
    name = fields.Char()

class Sample(models.Model):
    _name = 'terralab.sample'
    _description = 'TerraLab Sample'
    sample_type = fields.Many2one('terralab.sampletype', 'Sample Type') # Sample is of a specific SampleType
    tests = fields.One2many('terralab.test', 'sample', 'Tests') # Sample may have many Tests attached to it
    order = fields.Many2one('sale.order', 'Order') # Sample is always attached to an Order
    serial_number = fields.Char() # Freeform serial number to identity sample

    def name_get(self):
        return [(sample.id, '%s %s %s' % (sample.order.name, sample.sample_type.name, sample.serial_number)) for sample in self]

class TestVariableType(models.Model):
    _name = 'terralab.testvariabletype'
    _description = 'TerraLab Test Variable Type'
    test_type = fields.Many2one('product.template', 'Test Type') # Test Variable Types are attached to a specific TestType (Product)
    test_variables = fields.One2many('terralab.testvariable', 'test_variable_type', 'Test Variables') # There are many TestVariables of one TestVariableType
    name = fields.Char()

class TestVariable(models.Model):
    _name = 'terralab.testvariable'
    _description = 'TerraLab Test Variable'
    sample = fields.Many2one('terralab.sample', 'Sample') # Every TestVariable is attached to a specific Sample
    test = fields.Many2one('terralab.test', 'Test') # Every TestVariable is attached to a specific Test
    test_variable_type = fields.Many2one('terralab.testvariabletype', 'Test Variable Type') # Every TestVariable has a specific TestVariableType
    value = fields.Char()

# Note: Test Types are actually products
class TestType(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'
    terralab_test_variable_types = fields.One2many('terralab.testvariabletype', 'test_type', 'TerraLab TestVariable Types') # Test Types have a number of Test Variable Types, used to create Test Variables for Tests
    terralab_sample_type = fields.Many2one('terralab.sampletype', 'TerraLab Sample Type') # Test Types have a SampleType, so that a Test can be attached to Samples of that type
    terralab_test_name = fields.Char()

class Test(models.Model):
    _name = 'terralab.test'
    _description = 'TerraLab test'
    test_type = fields.Many2one('product.template', 'Test Type')
    sample = fields.Many2one('terralab.sample', 'Sample') # A Test is attached to a specific Sample
    test_variables = fields.One2many('terralab.testvariable', 'test', 'Test Variables') # A Test has a number of Test Variables
    test_result = fields.Char()

    def name_get(self):
        return [(test.id, '%s %s %s %s' % (test.sample.order.name, test.sample.sample_type.name, test.sample.serial_number, test.test_type.name)) for test in self]

# Extend Odoo Order
class Order(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'
    terralab_status = fields.Selection([
        ('pending_accept', 'Pending Accept'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
    ], string='TerraLab Status', default=None)
    terralab_samples = fields.One2many('terralab.sample', 'order', 'TerraLab Samples') # All Samples attached to this Order

    @api.model
    def create(self, values):
        Product = self.env['product.template']
        OrderLine = self.env['sale.order.line']
        TestVariable = self.env['terralab.testvariable']
        order = super(Order, self).create(values)
        logger.info('Creating Order %s' % (values))
        # Create Order Lines for all Tests
        for sample in order.terralab_samples:
            logger.info('Checking Order Sample %s' % (sample))
            for test in sample.tests:
                # Find TestType of test
                logger.info('Checking Order Sample Test %s' % (test))
                test_type = Product.browse(test.test_type.id)
                logger.info('Test Type: %s' % (test_type))
                # Create Order Line for this Test
                logger.info('Creating Order Line for Order %s Test %s' % (order.id, test))
                order_line = OrderLine.create({
                    'order_id': order.id,
                    'product_id': test_type.id,
                    'name': test_type.name,
                    'product_uom': test_type.uom_id.id,
                })
                order_line.product_id_change()
                # Create Test Variables for this Test
                for test_variable_type in test_type.terralab_test_variable_types:
                    logger.info('Creating Test Variable for Test Variable Type: %s' % (test_variable_type))
                    TestVariable.create({
                        'test_variable_type': test_variable_type.id,
                        'sample': sample['id'],
                        'test': test['id'],
                    })
        return order

    def write(self, values):
        super(Order, self).write(values)
        logger.info('Writing Order %s' % (values))
        return True

## Extend Odoo Order Line
#class OrderLine(models.Model):
#    _name = 'sale.order.line'
#    _inherit = 'sale.order.line'
#    terralab_test = fields.Many2one('terralab.test', 'TerraLab Test')
#
#    @api.model
#    def create(self, values):
#        res_id = super(OrderLine, self).create(values)
#        logger.info('Creating Order Line %s' % (values))
#        return res_id
#
#    def write(self, values):
#        super(OrderLine, self).write(values)
#        logger.info('Writing Order Line %s' % (values))
#        return True

class Report(models.Model):
    _name = 'terralab.report'
    _description = 'TerraLab Report'
    order = fields.Many2one('sale.order', 'Order') # A Report is attached to a specific Order
    pdf_url = fields.Char()
