using eShop.EventBus.Abstractions;
using System.Diagnostics;
namespace eShop.WebApp.Services.OrderStatus.IntegrationEvents;

public class OrderStatusChangedToSubmittedIntegrationEventHandler(
    OrderStatusNotificationService orderStatusNotificationService,
    ILogger<OrderStatusChangedToSubmittedIntegrationEventHandler> logger)
    : IIntegrationEventHandler<OrderStatusChangedToSubmittedIntegrationEvent>
{
    private static readonly ActivitySource _activitySource = new("eShop.WebApp.Services.OrderStatus.IntegrationEvents.OrderStatusChangedToSubmittedIntegrationEventHandler");

    public async Task Handle(OrderStatusChangedToSubmittedIntegrationEvent @event)
    {
        using var activity = _activitySource.StartActivity("OrderStatusChangedToSubmittedIntegrationEvent Handler");
        activity?.SetTag("order.orderId", @event.OrderId);
        activity?.SetTag("order.orderStatus", @event.OrderStatus);
        activity?.SetTag("buyerId", @event.BuyerIdentityGuid);

        logger.LogInformation("Handling integration event: {IntegrationEventId} - ({@IntegrationEvent})", @event.Id, @event);
        await orderStatusNotificationService.NotifyOrderStatusChangedAsync(@event.BuyerIdentityGuid);
    }
}
